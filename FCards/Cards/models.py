from django.db import models
from . import langcodes
from django.contrib.auth.models import User
# from googletrans import Translator
# from django.db.models import F


# Create your models here.

class CardFolder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    create_date = models.DateField(auto_now_add=True)
    edit_date = models.DateField(auto_now=True)
    lang1 = models.CharField(max_length=5, choices=langcodes.LangCodes0, default="en")
    lang2 = models.CharField(max_length=5, choices=langcodes.LangCodes0, default="pl")
    lang3 = models.CharField(max_length=5, choices=langcodes.LangCodes, default="ja", blank=True)
    lang4 = models.CharField(max_length=5, choices=langcodes.LangCodes, default="es", blank=True)
    lang5 = models.CharField(max_length=5, choices=langcodes.LangCodes, default="de", blank=True)
    score = models.SmallIntegerField(default=0)
    comment = models.CharField(max_length=400, blank=True)
    public = models.BooleanField(default=False)
    show_multicard_comment = models.BooleanField(default=True)

    def get_langs(self, item=False):
        langs = (self.lang1, self.lang2, self.lang3, self.lang4, self.lang5)
        lang_choices = []
        lang_values = []
        lang_keys = []
        for i in langs:
            if i != "":
                value = langcodes.LangCodesDict[i].capitalize()
                lang_choices.append((i, value))
                lang_values.append(value)
                lang_keys.append(i)
        if item == 'value':
            return lang_values
        if item == 'key':
            return lang_keys
        else:
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
    rates = models.SmallIntegerField(default=0)
    rating = models.SmallIntegerField(default=0)
    mastered = models.BooleanField(default=False)
    priority = models.SmallIntegerField(default=10)

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

    def check_if_mastered(self):
        langs = self.cards_folder.get_langs(item='key')
        mastered = True
        for lang in langs:
            if not Card.objects.get(multi_card=self, language=lang).mastered:
                mastered = False
        self.mastered = mastered
        self.save()

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
    priority = models.SmallIntegerField(default=0)
    show_answer = models.BooleanField(default=True)

    def check_show(self):
        # If card has been showed only for the game or if it is it's first appearance it will by un-showed.
        # If card is mastered, nothing changes.
        if not self.mastered:
            if self.score < 10:
                self.score = 10
            self.show_answer = False
            self.save()

    def check_answer(self, word_to_check):
        word_to_check = word_to_check.capitalize()
        # If answer is correct
        if word_to_check and (word_to_check == self.main or word_to_check == self.synonyms):
            points = 20
            self.score += 20
            self.multi_card.score += 20
            self.multi_card.priority += 1
            self.priority += 1
        # If answer is incorrect
        else:
            points = -15
            self.score -= 15

        self.update_numbers()

        return points

    def update_numbers(self):
        if self.score > 100:
            self.score = 100
            self.mastered = True
            self.show_answer = True
            self.multi_card.check_if_mastered()
        elif self.score < 85:
            self.mastered = False
            if self.score < 10:
                self.show_answer = True
                if self.score < 0:
                    self.score = 0
        if self.priority < 2:
            self.priority = 2
        # MultiCard.objects.filter(cards_folder=self.cards_folder).update(priority=F('priority') - 1)
        if self.multi_card.priority < 2:
            self.multi_card.priority = 2
        self.multi_card.save()
        self.save()

    def add_score_flashcards(self, score_priority):
        self.score += score_priority[0]
        self.multi_card.score += score_priority[0]
        self.multi_card.priority = score_priority[1]
        self.priority = score_priority[1]

        self.update_numbers()

    def __str__(self):
        return self.main
