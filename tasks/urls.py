from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # path("list/", views.TaskListView.as_view(), name="list"),
    path("list/", views.tasks_by_tag, name="list"),
    path("list/tag/<slug:tag_slug>", views.tasks_by_tag, name="list_by_tag"),
    # path("change_trello/<int:uid>", views.change_trello, name='change_trello'),
    path("details/<int:pk>", views.TaskDetailView.as_view(), name='details'),
    path("create/", views.TaskCreateView.as_view(), name="create"),
    path("add-task/", views.add_task, name="api-add-task"),
    path("complete/<int:uid>", views.complete_task, name="complete"),
    path("delete/<int:uid>", views.delete_task, name="delete"),
    path('edit/<int:pk>', views.TaskEditView.as_view(), name='edit'),
    path("export/", views.TaskExportView.as_view(), name="export"),
    path("import_from_trello/", views.add_tasks_from_trello, name='trello'),
]
