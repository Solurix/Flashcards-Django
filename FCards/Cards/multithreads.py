from googletrans import Translator
from .models import CardFolder, MultiCard, Card


def edit_folder_translate(folder):
    for multicard in folder.multicard_set.all():
        cards = multicard.card_set.all()
        created_langs = []
        for card in cards:
            created_langs.append(card.language)
        for lang in folder.langs_keys():
            if lang not in created_langs:
                first = cards.first()
                translation = Translator().translate(text=first.main, src=first.language, dest=lang)
                data = {'main': translation.text}
                if translation.pronunciation != first.main:
                    data['pronunciation'] = translation.pronunciation
                    data['automated'] = True
                Card.objects.create(multi_card=multicard, cards_folder=folder, language=lang, **data)
            # else:
            #     multicard.check_if_mastered()
            # got error when it was on this level
        else:
            multicard.check_if_mastered()
            # TODO it could probably be improved


def add_multicard_translate(langs, request, m_card, folder):
    origin = request.POST['main' + langs[0]].capitalize()
    for key in langs:
        data = {'main': request.POST['main' + key].capitalize(),
                'pronunciation': request.POST['pronunciation' + key].capitalize(),
                'synonyms': request.POST['synonyms' + key].capitalize(),
                'comment': request.POST['comment' + key]}
        if not data['main']:
            translation = Translator().translate(text=origin, src=langs[0], dest=key)
            data['main'] = translation.text
            if translation.pronunciation != origin:
                data['pronunciation'] = translation.pronunciation
            data['automated'] = True
        Card.objects.create(multi_card=m_card, language=key, cards_folder=folder, **data)


def add_many_translate(new_langs, word, language, m_card, folder):
    for lang in new_langs:
        translation = Translator().translate(text=word, src=language, dest=lang)
        data = {'main': translation.text.capitalize(),
                'language': lang,
                'synonyms': "",
                'comment': "",
                'pronunciation': "",
                'automated': True}
        if translation.pronunciation and translation.pronunciation != word:
            data['pronunciation'] = translation.pronunciation.capitalize()
        else:
            data['pronunciation'] = ""
        Card.objects.create(multi_card=m_card, cards_folder=folder, **data)
        # TODO Because of multi-threading user data may be overwritten. Especially in edit_many view.
