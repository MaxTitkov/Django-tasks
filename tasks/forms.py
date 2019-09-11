from django import forms
from trello import TrelloClient

from tasks.models import TodoItem

class AddTrelloIdForm(forms.Form):
    board_id = forms.CharField(max_length=24, label="Trello board ID", initial='5d41cf7defc9fe1b3d23e7f9')

class AddTaskForm(forms.Form):
    description = forms.CharField(max_length=64, label="")


class TodoItemForm(forms.ModelForm):
    class Meta:
        model = TodoItem
        fields = ('description', 'priority', 'tags')
        labels = {"description": "Описание",
                  "priority": "",
                  "tags": "теги",
                  }


class TodoItemExportForm(forms.Form):
    prio_high = forms.BooleanField(label='Высокая важность', initial=True, required=False)
    prio_med = forms.BooleanField(label='Средняя важность', initial=True, required=False)
    prio_low = forms.BooleanField(label='Низкая важность', initial=False, required=False)
