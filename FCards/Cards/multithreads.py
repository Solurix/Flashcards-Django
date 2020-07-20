from googletrans import Translator
from .models import CardFolder, MultiCard, Card


# from signal import signal
#
# def _handler(signum, frame):
#     print("Forever is over!")
#     raise Exception("end of time")

def edit_folder_translate(folder):
    folder.being_edited = True
    folder.save()
    for multicard in folder.multicard_set.all():
        cards = multicard.card_set.all()
        created_langs = []
        for card in cards:
            created_langs.append(card.language)
        for lang in folder.langs_keys():
            if lang not in created_langs:
                first = cards.first()
                translation = Translator().translate(text=first.main, src=first.language, dest=lang)

                # Repeat if failed
                if not translation.text:
                    translation = Translator().translate(text=first.main, src=first.language, dest=lang)
                data = {'main': translation.text.capitalize()}

                # If still failed
                if not data['main']:
                    data['main'] = 'Translation error'
                else:
                    data['automated'] = True
                if translation.pronunciation != first.main and translation.pronunciation != "None":
                    data['pronunciation'] = translation.pronunciation

                Card.objects.create(multi_card=multicard, cards_folder=folder, language=lang, **data)
            # else:
            #     multicard.check_if_mastered()
            # got error when it was on this level
        else:
            multicard.check_if_mastered()
            # TODO it could probably be improved
        folder.being_edited = False
        folder.save()
    clean_errors(folder)


def add_multicard_translate(langs, request, m_card, folder):
    m_card.being_edited = True
    m_card.save()
    origin = request.POST['main' + langs[0]].capitalize()
    for key in langs:
        data = {'main': request.POST['main' + key].capitalize(),
                'pronunciation': request.POST['pronunciation' + key].capitalize(),
                'synonyms': request.POST['synonyms' + key].capitalize(),
                'comment': request.POST['comment' + key]}
        if not data['main']:
            translation = Translator().translate(text=origin, src=langs[0], dest=key)

            # Repeat if failed
            if not translation.text:
                translation = Translator().translate(text=origin, src=langs[0], dest=key)
            data['main'] = translation.text.capitalize()

            # If still failed
            if not data['main']:
                data['main'] = 'Translation error'

            if translation.pronunciation != origin:
                data['pronunciation'] = translation.pronunciation
            data['automated'] = True
        Card.objects.create(multi_card=m_card, language=key, cards_folder=folder, **data)
    m_card.being_edited = False
    m_card.save()


def add_many_translate(new_langs, word, language, m_card, folder):
    m_card.being_edited = True
    m_card.save()
    for lang in new_langs:
        translation = Translator().translate(text=word, src=language, dest=lang)
        data = {'main': translation.text.capitalize(),
                'language': lang,
                'synonyms': "",
                'comment': "",
                'pronunciation': "",
                'automated': True}

        # Repeat if failed
        if not data['main']:
            translation = Translator().translate(text=word, src=language, dest=lang)
            if not translation.text:
                data['main'] = 'Translation error'
            else:
                data['main'] = translation.text
                if translation.pronunciation and translation.pronunciation != word:
                    data['pronunciation'] = translation.pronunciation.capitalize()
                else:
                    data['pronunciation'] = ""
        Card.objects.create(multi_card=m_card, cards_folder=folder, **data)
    m_card.being_edited = False
    m_card.save()
    # TODO Because of multi-threading user data may be overwritten. Especially in edit_many view.


def _clean_doubles(folder):
    for multi_card in MultiCard.objects.filter(cards_folder=folder):
        for lang in folder.langs_keys():
            card_check = Card.objects.filter(language=lang, multi_card=multi_card)
            while len(Card.objects.filter(language=lang, multi_card=multi_card)) > 1:
                print(card_check)
                if card_check[0].automated:
                    card_check[0].delete()
                else:
                    card_check[1].delete()


def _clean_empty(folder):
    for multi_card in MultiCard.objects.filter(cards_folder=folder):
        for lang in folder.langs_keys():
            try:
                Card.objects.get(multi_card=multi_card, language=lang)
            except Card.DoesNotExist:
                if lang == folder.lang1:
                    multi_card.delete()
                    continue
                else:
                    data = {
                        'multi_card': multi_card, 'cards_folder': folder, 'language': lang,
                        'main': 'Translation error'
                    }
                    Card.objects.create(**data)

        else:
            for card in Card.objects.filter(multi_card=multi_card):
                if card.main == "":
                    if card.language == folder.lang1:
                        multi_card.delete()
                        continue
                    else:
                        card.main = 'Translation error'
                card.save()
        multi_card.being_edited = False
        multi_card.save()


def clean_errors(folder):
    _clean_doubles(folder)
    _clean_empty(folder)
    folder.being_edited = False
    folder.save()


def repair_translations_thread(folder):
    print(Card.objects.filter(cards_folder=folder, main='Translation error'))
    for card in Card.objects.filter(cards_folder=folder, main='Translation error'):
        card_main_lang = Card.objects.get(multi_card=card.multi_card, language=folder.lang1)
        translation = Translator().translate(text=card_main_lang.main, src=folder.lang1, dest=card.language)
        # Repeat if failed
        if not translation.text:
            translation = Translator().translate(text=card_main_lang.main, src=folder.lang1, dest=card.language)
        if not translation.text:
            card.main = 'Translation error'
        else:
            card.main = translation.text
            card.automated = True
            if not type(translation.pronunciation) == list:
                if translation.pronunciation and translation.pronunciation != card_main_lang.main:
                    print(card.main)
                    print(translation.pronunciation)
                    card.pronunciation = translation.pronunciation.capitalize()
                else:
                    card.pronunciation = ""
        card.save()
