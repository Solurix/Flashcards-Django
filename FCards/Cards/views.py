from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import CardFolder, MultiCard, Card
from .forms import FolderForm, CardsForm
from googletrans import Translator
import random as rd


# from django.http import HttpResponse
# from django.template import loader
# from django.forms import formset_factory


@login_required
def home(request):
    return render(request, 'Cards/index.html')


@login_required
def delete_folder(request, set_id):
    if request.method == 'POST':
        folder = CardFolder.objects.get(id=set_id)
        folder.delete()
        return render(request, 'Cards/index.html')
    else:
        return render(request, 'Cards/index.html')


@login_required
def add_folder(request):
    form = FolderForm(request.POST or None)
    if form.is_valid():
        if request.method == "POST":
            CardFolder.objects.create(user=request.user, **form.cleaned_data)
            return render(request, 'Cards/index.html')

    context = {
        "form": form
    }
    return render(request, 'Cards/add_set.html', context)


@login_required
def edit_folder(request, set_id):
    folder = get_object_or_404(CardFolder, id=set_id)
    user_folders = request.user.cardfolder_set.all()
    if folder in user_folders:
        if request.method == 'POST':
            form = FolderForm(request.POST or None, instance=folder)
            if form.is_valid():
                folder = form.save(commit=False)
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
                            data = {'main': translation.text}
                            if translation.pronunciation != first.main:
                                data['pronunciation'] = translation.pronunciation
                                data['automated'] = True
                            Card.objects.create(multi_card=multicard, cards_folder=folder, language=lang, **data)
                return render(request, 'Cards/index.html')

        else:
            form = FolderForm(instance=folder)
        return render(request, 'Cards/edit_set.html', {'form': form})
    else:
        return render(request, 'Cards/no_access.html')


@login_required
def add_multicard(request, set_id):
    folder = get_object_or_404(CardFolder, id=set_id)
    user_folders = request.user.cardfolder_set.all()
    langs = folder.get_langs()
    length = len(langs)
    form = CardsForm(request.POST or None)
    data = {}
    if folder in user_folders:
        if request.method == "POST":
            if request.POST['main' + langs[0][0]]:
                m_card = MultiCard.objects.create(cards_folder=folder, comment=request.POST['comment'],
                                                  definition=request.POST['definition'])
                m_card.save()
                for k, v in langs:
                    data[k] = {'main': request.POST['main' + k].capitalize(),
                               'pronunciation': request.POST['pronunciation' + k].capitalize(),
                               'synonyms': request.POST['synonyms' + k].capitalize(),
                               'comment': request.POST['comment' + k]}
                    if not data[k]['main']:
                        translation = Translator().translate(text=data[langs[0][0]]["main"], src=langs[0][0], dest=k)
                        data[k]['main'] = translation.text
                        if translation.pronunciation != data[langs[0][0]]["main"]:
                            data[k]['pronunciation'] = translation.pronunciation
                        data[k]['automated'] = True
                    Card.objects.create(multi_card=m_card, language=k, cards_folder=folder, **data[k])
            return redirect(request.META['HTTP_REFERER'])
        context = {
            "form": form,
            'folder': folder,
            "length": length,
            "langs": langs,
        }
        return render(request, 'Cards/add_multicard.html', context)
    else:
        return render(request, 'Cards/no_access.html')


@login_required
def add_many(request, set_id):
    folder = get_object_or_404(CardFolder, id=set_id)
    user_folders = request.user.cardfolder_set.all()
    langs = folder.get_langs()
    length = len(langs)
    form = CardsForm(request.POST or None)
    # data = {}
    if folder in user_folders:
        if request.method == "POST":
            separator = str(request.POST['separator'])
            language = str(request.POST['language'])
            for_translate = request.POST['for_translate']
            if not separator or not language or not for_translate:
                return render(request, 'Cards/no_access.html')
            new_cards = for_translate.split(separator)
            new_langs = folder.langs_keys()
            new_langs.remove(language)
            for word in new_cards:
                m_card = MultiCard.objects.create(cards_folder=folder)
                m_card.save()
                word = word.capitalize()
                Card.objects.create(multi_card=m_card, cards_folder=folder, language=language, main=word, synonyms="",
                                    comment="", pronunciation="")
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

            return redirect(request.META['HTTP_REFERER'])
        context = {
            "form": form,
            'folder': folder,
            "length": length,
            "langs": langs,
        }
        return render(request, 'Cards/add_many.html', context)
    else:
        return render(request, 'Cards/no_access.html')


@login_required
def edit_multicards(request, set_id):
    folder = get_object_or_404(CardFolder, id=set_id)
    langs = folder.get_langs()
    length = len(langs)
    context = {
        # "form": form,
        'folder': folder,
        "length": length,
        "langs": langs,
        'width': 94 / length
    }
    return render(request, 'Cards/edit_multicards.html', context)


@login_required
def edit_multicards_save(request, set_id, m_card_id):
    if request.method == "POST":
        folder = get_object_or_404(CardFolder, id=set_id)
        langs = folder.get_langs()
        m_card = get_object_or_404(MultiCard, id=m_card_id)
        m_id = str(m_card.id)
        m_card.definition = request.POST['definition' + m_id]
        m_card.comment = request.POST['comment' + m_id]
        m_card.save()
        for k, v in langs:
            card = Card.objects.get(multi_card=m_card, language=k)
            if request.POST['main' + k + m_id] != card.main:
                card.automated = False
            card.main = request.POST['main' + k + m_id].capitalize()
            card.pronunciation = request.POST['pronunciation' + k + m_id].capitalize()
            card.synonyms = request.POST['synonyms' + k + m_id].capitalize()
            card.comment = request.POST['comment' + k + m_id]
            card.save()
        return HttpResponse(status=204)
    else:
        return render(request, 'Cards/no_access.html')


@login_required
def edit_all_multicards(request, set_id):
    folder = get_object_or_404(CardFolder, id=set_id)
    user_folders = request.user.cardfolder_set.all()
    langs = folder.get_langs()
    length = len(langs)
    context = {
        'folder': folder,
        "length": length,
        "langs": langs,
        'width': 94 / length
    }
    if request.method == "POST":
        # m_card = get_object_or_404(MultiCard, id=m_card_id)
        for m_card in folder.multicard_set.all():
            m_id = str(m_card.id)
            if request.POST.get(('delete' + m_id), False):
                m_card.delete()
            else:
                m_card.definition = request.POST['definition' + m_id]
                m_card.comment = request.POST['comment' + m_id]
                m_card.save()
                for k, v in langs:
                    card = Card.objects.get(multi_card=m_card, language=k)
                    if request.POST['main' + k + m_id] != card.main:
                        card.automated = False
                    card.main = request.POST['main' + k + m_id].capitalize()
                    card.pronunciation = request.POST['pronunciation' + k + m_id].capitalize()
                    card.synonyms = request.POST['synonyms' + k + m_id].capitalize()
                    card.comment = request.POST['comment' + k + m_id]
                    card.save()
        return render(request, 'Cards/edit_all_multicards.html', context)
    else:
        if folder not in user_folders:
            return render(request, 'Cards/no_access.html')
        else:
            return render(request, 'Cards/edit_all_multicards.html', context)


@login_required
def delete_multicards(request, set_id, m_card_id):
    if request.method == "POST":
        m_card = get_object_or_404(MultiCard, id=m_card_id)
        m_card.delete()
        folder = get_object_or_404(CardFolder, id=set_id)
        langs = folder.get_langs()
        length = len(langs)
        context = {
            'folder': folder,
            "length": length,
            "langs": langs,
            'width': 94 / length
        }
        return render(request, 'Cards/edit_multicards.html', context)
    else:
        return render(request, 'Cards/no_access.html')


@login_required
def play(request, set_id):
    folder = get_object_or_404(CardFolder, id=set_id)
    user_folders = request.user.cardfolder_set.all()
    if folder not in user_folders:
        return render(request, 'Cards/no_access.html')
    langs = folder.get_langs()
    lang_keys = folder.langs_keys
    length = len(langs)
    context = {
        'previous': False,
        'folder': folder,
        "length": length,
        "langs": langs,
        'width': 94 / length,
    }

    if request.method == "POST":
        previous_cards = []
        for lang, values in langs:
            if lang == request.POST['show_language']:
                pass
            else:
                card_id = request.POST['id'+lang]
                answer = request.POST['answer'+lang]
                card = Card.objects.get(id=card_id)
                points = card.check_multi_input(answer)
                if not answer:
                    answer = 'No answer'
                if points > 0:
                    true_false = True
                else:
                    true_false = False
                previous_cards.append([card, true_false, answer, values])

        multicard_id = int(request.POST['multicard_id'])
        context['previous'] = MultiCard.objects.get(id=multicard_id)
        context['previous_show'] = request.POST['show_card']
        context['previous_cards'] = previous_cards

    m_card = MultiCard.objects.filter(cards_folder=folder, mastered=False).order_by('priority', 'score')
        # TODO add that there are no cards in the set or all cards are mastered.
        # TODO remove card that just has been studied
    m_card = m_card.first()
    if m_card is None:
        return render(request, 'Cards/index.html', context)

    cards = []
    for key in lang_keys():
        cards.append(Card.objects.get(multi_card=m_card, language=key))
    show_card = rd.choice(cards)
    hidden_cards = cards
    hidden_cards.remove(show_card)
    context['m_card'] = m_card
    context['show_card'] = show_card
    context['cards'] = cards
    context['hidden_cards'] = hidden_cards

    return render(request, 'Cards/play.html', context)
