from django.db import models
from . import langcodes
from django.contrib.auth.models import User
from googletrans import Translator


# Create your models here.

class CardFolder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    create_date = models.DateField(auto_now_add=True)
    edit_date = models.DateField(auto_now=True)
    lang1 = models.CharField(max_length=5, choices=langcodes.LangCodes, default="en")
    lang2 = models.CharField(max_length=5, choices=langcodes.LangCodes, default="pl")
    lang3 = models.CharField(max_length=5, choices=langcodes.LangCodes, default="ja", blank=True)
    lang4 = models.CharField(max_length=5, choices=langcodes.LangCodes, default="es", blank=True)
    lang5 = models.CharField(max_length=5, choices=langcodes.LangCodes, default="de", blank=True)
    score = models.IntegerField(default=0)
    comment = models.CharField(max_length=400, blank=True)

    def get_langs(self):
        langs = (self.lang1, self.lang2, self.lang3, self.lang4, self.lang5)
        lang_choices = []
        for i in langs:
            if i != "":
                lang_choices.append((i, langcodes.LangCodesDict[i]))
        return lang_choices

    def langs_keys(self):
        langs = [self.lang1, self.lang2, self.lang3, self.lang4, self.lang5]
        true_langs = []
        for i in langs:
            if i != "":
                true_langs.append(i)
        return true_langs

    def langs_no(self):
        return len(self.get_langs())

    langs_no.short_description = "No of languages"

    def __str__(self):
        return self.name


class MultiCard(models.Model):
    cards_folder = models.ForeignKey(CardFolder, on_delete=models.CASCADE)
    score = models.SmallIntegerField(default=0)
    comment = models.CharField(max_length=400, blank=True)
    definition = models.CharField(max_length=400, blank=True)
    rates = models.IntegerField(default=0)
    rating = models.IntegerField(default=0)
    mastered = models.BooleanField(default=False)
    priority = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id)

    def max_languages(self):
        return self.cards_folder.langs_no()

    def all_translations(self):
        mains = []
        cards = self.card_set.all()
        for card in cards:
            mains.append(card.language + ": " + card.main)
        return mains

    # image = models.ImageField(upload_to='uploads/')
    # choice_text = models.CharField(max_length=200)
    # votes = models.IntegerField(default=0)


class Card(models.Model):
    multi_card = models.ForeignKey(MultiCard, on_delete=models.CASCADE)
    cards_folder = models.ForeignKey(CardFolder, on_delete=models.CASCADE)
    language = models.CharField(max_length=5, choices=langcodes.LangCodes, default="en")
    main = models.CharField(max_length=50)
    automated = models.BooleanField(default=False)
    score = models.SmallIntegerField(default=0)
    pronunciation = models.CharField(max_length=200, blank=True, default=False, null=True)
    synonyms = models.CharField(max_length=50, blank=True)
    comment = models.CharField(max_length=400, blank=True)
    rating = models.SmallIntegerField(default=0)
    mastered = models.BooleanField(default=False)
    priority = models.IntegerField(default=0)

    def check_multi_input(self, word_to_check):
        word_to_check = word_to_check.capitalize()
        if word_to_check == self.main:
            points = 20
            self.score += 20
            self.multi_card.score += 20
            self.multi_card.priority += 1
            if self.score > 100:
                self.score = 100
                self.mastered = True
            self.priority += 1
        else:
            points = -15
            self.score -= 15
            if self.score < 85:
                self.score = 0
                self.mastered = False
            self.priority -= 1
            self.multi_card.score -= 15
            self.multi_card.priority -= 1
        if self.priority < 2:
            self.priority = 2
        self.multi_card.save()
        self.save()
        return points

    def __str__(self):
        return self.main
