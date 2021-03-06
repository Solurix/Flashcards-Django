from django.forms import ModelForm
from .models import CardFolder
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class FolderForm(ModelForm):
    class Meta:
        model = CardFolder
        fields = ['name', 'lang1', 'lang2', 'lang3', 'lang4', 'lang5', 'comment']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Name for the set')}),
            'lang1': forms.Select(attrs={'class': 'form-control'}),
            'lang2': forms.Select(attrs={'class': 'form-control'}),
            'lang3': forms.Select(attrs={'class': 'form-control'}),
            'lang4': forms.Select(attrs={'class': 'form-control'}),
            'lang5': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'name': _('Set name'),
            'lang1': _('1st language'),
            'lang2': _('2nd language'),
            'lang3': _('3rd language'),
            'lang4': _('4th language'),
            'lang5': _('5th language'),
            'comment': _('Your comment'),
        }

    def clean(self):
        cleaned_data = super().clean()
        lang1 = cleaned_data.get("lang1")
        lang2 = cleaned_data.get("lang2")
        lang3 = cleaned_data.get("lang3")
        lang4 = cleaned_data.get("lang4")
        lang5 = cleaned_data.get("lang5")

        langs = []
        for lang in (lang1, lang2, lang3, lang4, lang5):
            if lang:
                langs.append(lang)

        def check_if_duplicates(listOfElems):
            ''' Check if given list contains any duplicates '''
            if len(listOfElems) == len(set(listOfElems)):
                return False
            else:
                return True

        result = check_if_duplicates(langs)
        if result:
            raise ValidationError(_("Every language must be different."))


class CardsForm(forms.Form):
    # MultiCard
    # multi_comment = forms.CharField(max_length=400, required=False, widget=forms.TextInput(attrs={'class': 'form'
    #                                                                                                        '-control'}))
    # multi_definition = forms.CharField(max_length=400, required=False, widget=forms.TextInput(attrs={'class': 'form'
    #                                                                                                           '-control'}))

    # Card
    language = forms.CharField(max_length=5)
    main = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    automated = forms.BooleanField(initial=False)
    pronunciation = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form'
                                                                                                           '-control'}))
    synonyms = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    comment = forms.CharField(max_length=400, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    # class Meta:
    #     widgets = {
    #         'automated': forms.HiddenInput(),
    #         'language': forms.HiddenInput(),
    #         'main': forms.CharField(attrs={'class': 'form-control'}),
    #         'pronunciation': forms.CharField(attrs={'class': 'form-control'}),
    #         'synonyms': forms.CharField(attrs={'class': 'form-control'}),
    #         'comment': forms.CharField(attrs={'class': 'form-control'}),}

    # def __init__(self, *args, **kwargs):
    #     super(RawCardForm, self).__init__(*args, **kwargs)
    #     self.fields['language'] = forms.ChoiceField(
    #         choices=get_my_choices() )
