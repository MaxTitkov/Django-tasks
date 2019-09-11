from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views import View
from .forms import LoginForm, RegistrationForm, UserEditForm, ProfileEditForm
from django.http import HttpResponse
from django.shortcuts import render
from .models import Profile
from django.contrib import messages

class LoginView(View):
    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request,
                username = cd['username'],
                password = cd['password']
            )

            if user is None:
                return HttpResponse('Please, register')

            if not user.is_active:
                return HttpResponse('Youre blocked')

            login(request, user)
            return HttpResponse('Youre logged in!')
        return render(request, 'accounts/login.html', {'form': form})

    def get(self, request, *args, **kwargs):
        form = LoginForm()
        return render(request, 'accounts/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_user = form.save(commit=False)
            new_user.set_password(cd['password'])
            new_user.save()
            Profile.objects.create(user=new_user)

            return render(request, 'accounts/registration_complete.html', {'new_user': new_user})
    else:
        form = RegistrationForm()

    return render(request, 'accounts/registration.html', {'user_form': form})

@login_required
def edit(request):
    if request.method == "POST":
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)

        profile_form = ProfileEditForm(
            instance=request.user.profile,
            data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            # if (profile_form.data['trello_api_key'] and profile_form.data['trello_api_secret']) is not None:
            #     messages.success(request, 'Risk')
            if (request.POST['trello_api_key']!= '' and request.POST['trello_api_secret']!= ''):
                messages.warning(request, 'Пожалуйста, удалите токены, когда они будут вам не нужны!')
            user_form.save()
            profile_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    return render(
        request,
        "accounts/edit.html",
        {"user_form": user_form, "profile_form": profile_form},
    )


# from django.core.mail import send_mail
# from django.conf import settings
#
# send_mail("Привет от django", "Письмо отправленное из приложения", settings.EMAIL_HOST_USER, ["maxim-titkov@yandex.ru"], fail_silently=False)
