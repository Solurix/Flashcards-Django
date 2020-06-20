from django.forms import ModelForm
from .models import CardFolder


class FolderForm(ModelForm):
    class Meta:
        model = CardFolder
        fields = ['name', 'lang1', 'lang2', 'lang3', 'lang4', 'lang5', 'comment']

