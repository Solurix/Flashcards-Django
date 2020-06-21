from django.forms import ModelForm
from .models import CardFolder, Card
from django import forms
from . import langcodes
from django.core.exceptions import ValidationError


class FolderForm(ModelForm):
    # name = forms.CharField(max_length=200, label="Set name:", widget=forms.TextInput(attrs={
    #     "placeholder": "Name for this set"}))
    class Meta:
        model = CardFolder
        fields = ['name', 'lang1', 'lang2', 'lang3', 'lang4', 'lang5', 'comment']

    def clean_name(self, *args, **kwargs):
        name = self.cleaned_data.get("name")
        if 'test' not in name:
            raise forms.ValidationError("must include 'test'")
        return name

    def clean(self):
        cleaned_data = super().clean()
        lang1 = cleaned_data.get("lang1")
        lang2 = cleaned_data.get("lang2")
        lang3 = cleaned_data.get("lang3")
        lang4 = cleaned_data.get("lang4")
        lang5 = cleaned_data.get("lang5")

        if lang1 == lang2 or (lang3 and (lang3 in (lang1, lang2))) or (lang4 and (lang4 in (lang1, lang2, lang3))) or \
                (lang5 and (lang5 in (lang1, lang2, lang3, lang4))):
            raise ValidationError("Every language must be different.")



# class RawFolderForm(forms.Form):
#     name = forms.CharField(max_length=200, label="Set name:", widget=forms.TextInput(attrs={
#         "placeholder": "Name for this set"}))
#     lang1 = forms.ChoiceField(label="Language 1", choices=langcodes.LangCodes, initial='en')
#     lang2 = forms.CharField(max_length=5, label="Language 2", widget=forms.TextInput(attrs={
#         "placeholder": "Language you want to learn"}))
#     lang3 = forms.CharField(max_length=5, label="Language 3", required=False, widget=forms.TextInput(attrs={
#         "placeholder": "Another language (optional)"}))
#     lang4 = forms.CharField(max_length=5, label="Language 4", required=False, widget=forms.TextInput(attrs={
#         "placeholder": "Another language (optional)"}))
#     lang5 = forms.CharField(max_length=5, label="Language 5", required=False, widget=forms.TextInput(attrs={
#         "placeholder": "Another language (optional)"}))
#     comment = forms.CharField(max_length=400, required=False, widget=forms.TextInput(attrs={
#         "placeholder": "You note (optional)"}))

# class RawCardForm(forms.ModelForm):
#     class Meta:
#         model = Card
#     multi_card = forms.ForeignKey(MultiCard, on_delete=models.CASCADE)
#     language = forms.CharField(max_length=5, choices=langcodes.LangCodes, default="en")
#     main = forms.CharField(max_length=50)
#     automated = forms.BooleanField(default=False)
#     score = forms.PositiveSmallIntegerField(default=0)
#     pronunciation = forms.CharField(max_length=200, blank=True)
#     synonyms = forms.CharField(max_length=50, blank=True)
#     comment = forms.CharField(max_length=400, blank=True)
#     rating = forms.SmallIntegerField(default=0)
#
#     def __init__(self, *args, **kwargs):
#         super(RawCardForm, self).__init__(*args, **kwargs)
#         self.fields['language'] = forms.ChoiceField(
#             choices=get_my_choices() )
