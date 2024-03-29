from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from todoapp.ru_taggit import RuTaggedItem


class TodoItem(models.Model):

    PRIORITY_HIGH = 1
    PRIORITY_MEDIUM = 2
    PRIORITY_LOW = 3
    PRIORITY_CHOICES = [(PRIORITY_HIGH, 'Высокий приоритет'),
                        (PRIORITY_MEDIUM, 'Средний приоритет'),
                        (PRIORITY_LOW, 'Низкий приоритет')]


    description = models.CharField(max_length=64)
    is_completed = models.BooleanField("выполнено", default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks')
    priority = models.IntegerField("Приоритет", choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)

    tags = TaggableManager(through=RuTaggedItem)

    trello_id = models.CharField(max_length=24, null=True, blank=True)
    task_id = models.CharField(max_length=24, null=True, blank=True)

    def __str__(self):
        return self.description.lower()

    class Meta:
        ordering = ('-created',)


