from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CardFolder, MultiCard, Card
import random as rd


@login_required
def play(request, set_id):
    folder = get_object_or_404(CardFolder, id=set_id)
    if folder.user != request.user:
        return render(request, 'Cards/no_access.html')
    langs = folder.get_langs()
    lang_keys = folder.langs_keys()
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
        previous_hidden = []
        previous_shown = []
        for lang in lang_keys:
            if request.POST['previous' + lang] == 'show':
                previous_shown.append(lang)
            else:
                previous_hidden.append(lang)
        for lang, full_lang in langs:
            card_id = request.POST['id' + lang]
            card = Card.objects.get(id=card_id)
            previous_card = {
                'lang': lang,
                'main': card.main,
                'language': full_lang,
            }
            if lang in previous_shown:
                previous_card['answer'] = False
            else:
                answer = request.POST['answer' + lang]
                points = card.check_multi_input(answer)
                if not answer:
                    answer = 'No answer'
                if points > 0:
                    previous_card['correct'] = True
                else:
                    previous_card['correct'] = False
            previous_cards.append(previous_card)

    multicard_id = int(request.POST['multicard_id'])
    previous_multicard = MultiCard.objects.get(id=multicard_id)
    m_cards = MultiCard.objects.filter(cards_folder=folder, mastered=False).order_by('priority', 'score')
    if context['previous']:
        m_cards = m_cards.exclude(id=context['previous'].id)
    # TODO add that there are no cards in the set or all cards are mastered.
    # TODO remove card that just has been studied
    m_card = m_cards.first()
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
    context['previous_cards'] = previous_cards

    return render(request, 'Cards/play.html', context)


"""
Game types:
1: Word in one language is shown. User has to write word in other languages.
2: Only one language is hidden.
"""
