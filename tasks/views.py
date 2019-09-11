from django.http import HttpResponse
from django.shortcuts import redirect, render, reverse, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView
from tasks.forms import AddTaskForm, TodoItemForm, TodoItemExportForm, AddTrelloIdForm
from tasks.models import TodoItem
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings

from trello import TrelloClient, Card
from accounts.models import Profile




@login_required
def index(request):
    return HttpResponse("Примитивный ответ из приложения tasks")


def complete_task(request, uid):
    t = TodoItem.objects.get(id=uid)
    t.is_completed = True
    t.save()
    return HttpResponse("OK")


def add_task(request):
    if request.method == "POST":
        desc = request.POST["description"]
        t = TodoItem(description=desc)
        t.save()
    return redirect("/tasks/list")


def delete_task(request, uid):
    t = TodoItem.objects.get(id=uid)
    t.delete()
    messages.success(request, 'Задача удалена')
    return redirect(reverse('list'))


def filter_tags(tags_by_task):
    tags_set = set()
    for tags_list in tags_by_task:
        for tag in tags_list:
            tags_set.add(tag)
    return sorted(tags_set)

class TaskListView(LoginRequiredMixin, ListView):
    # queryset = TodoItem.objects.all() ПЕРЕОПРЕДЕЛЯЕМ НИЖЕ!!!!
    context_object_name = "tasks"
    template_name = "tasks/list.html"

    def get_queryset(self):
        u = self.request.user
        return u.tasks.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_tasks = self.get_queryset()
        tags = []
        for task in user_tasks:
            tags.append(list(task.tags.all()))
        context["tags"] = filter_tags(tags)
        return context

class TaskDetailView(DetailView):
    template_name = 'tasks/details.html'
    model = TodoItem

class TaskCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = TodoItemForm(request.POST)
        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.owner = request.user
            new_task.save()
            form.save_m2m()
            return redirect(reverse('list'))

        return render(request, "tasks/create.html", {"form": form})

    def get(self, request, *args, **kwargs):
        form = TodoItemForm()
        return render(request, "tasks/create.html", {"form": form})


class TaskEditView(LoginRequiredMixin, View):

    def post(self, request, pk, *args, **kwargs):
        t = TodoItem.objects.get(id=pk)
        form = TodoItemForm(request.POST, instance=t)
        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.owner = request.user
            new_task.save()
            form.save_m2m()
            return redirect(reverse('list'))
        return render(request, 'tasks/edit.html', {'form': form, 'task': t})

    def get(self, request, pk, *args, **kwargs):
        t = TodoItem.objects.get(id=pk)
        form = TodoItemForm(instance = t)
        return render(request, 'tasks/edit.html', {'form': form, 'task': t})


class TaskExportView(LoginRequiredMixin, View):
    def generate_body(self, user, priorities):
        q = Q()
        if priorities["prio_high"]:
            q = q | Q(priority=TodoItem.PRIORITY_HIGH)
        if priorities["prio_med"]:
            q = q | Q(priority=TodoItem.PRIORITY_MEDIUM)
        if priorities["prio_low"]:
            q = q | Q(priority=TodoItem.PRIORITY_LOW)
        tasks = TodoItem.objects.filter(owner=user).filter(q).all()

        body = "Ваши задачи и приоритеты:\n"
        for t in list(tasks):
            if t.is_completed:
                body += f"[x] {t.description} ({t.get_priority_display()})\n"
            else:
                body += f"[ ] {t.description} ({t.get_priority_display()})\n"

        return body

    def post(self, request, *args, **kwargs):
        form = TodoItemExportForm(request.POST)
        if form.is_valid():
            email = request.user.email
            body = self.generate_body(request.user, form.cleaned_data)
            send_mail("Задачи", body, settings.EMAIL_HOST_USER, [email])
            messages.success(
                request, "Задачи были отправлены на почту %s" % email)
        else:
            messages.error(request, "Что-то пошло не так, попробуйте ещё раз")
        return redirect(reverse("list"))

    def get(self, request, *args, **kwargs):
        form = TodoItemExportForm()
        return render(request, "tasks/export.html", {"form": form})


def tasks_by_tag(request, tag_slug = None):
    u = request.user
    # tasks = TodoItem.objects.filter(owner=u).all()
    tasks = u.tasks.all()
    tag = None

    for task in tasks:
        if task.is_completed:
            change_task_list(request, task)

    if tag_slug:
        tag = get_object_or_404(Tag, tag_slug)
        tasks = tasks.filter(tags__in = [tag])
    return render(request, "tasks/list_by_tag.html", {"tag": tag, "tasks": tasks})

# def change_trello(request, uid):
#     u = request.user
#     # tasks = TodoItem.objects.filter(owner=u).all()
#     task = u.tasks.get(id=uid)
#     if task.is_completed:
#         change_task_list(request, task)
#     return redirect(reverse("list"))

def get_trello_tasks(board_id, api_key, api_secret):
    client = TrelloClient(api_key=api_key, api_secret=api_secret)
    todo_board = client.get_board(board_id=board_id)
    to_do = todo_board.list_lists()[0]
    tasks_list = to_do.list_cards()

    return tasks_list

def change_task_list(request, task):
    p = request.user.profile
    trello_key = p.trello_api_key
    trello_secret = p.trello_api_secret
    client = TrelloClient(api_key=trello_key, api_secret=trello_secret)
    todo_board = client.get_board(board_id=task.trello_id)
    last_list = todo_board.list_lists()[-1]
    card = Card(card_id = str(task.task_id), parent = todo_board)
    card.change_list(list_id=str(last_list.id))


def add_tasks_from_trello(request):
    p = request.user.profile
    trello_key = p.trello_api_key
    trello_secret= p.trello_api_secret

    if request.method == "POST":
        form = AddTrelloIdForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            trello_id = cd["board_id"]

            tasks = get_trello_tasks(board_id = trello_id, api_key=trello_key, api_secret=trello_secret)

            for task in tasks:
                t = TodoItem(description = task.name, trello_id = task.board_id, task_id = task.id)
                t.owner = request.user
                t.save()
            return redirect(reverse('list'))
    else:
        form = AddTrelloIdForm()

    return render(request, "tasks/AddTrelloId.html", {"form": form})

