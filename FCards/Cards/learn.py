from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import CardFolder, MultiCard, Card
import random as rd


@login_required
def learn(request, set_id):
    folder = get_object_or_404(CardFolder, id=set_id)
    enough = len(folder.multicard_set.all()) > 2
    context = {'folder': folder, 'enough': enough}
    if folder.user != request.user:
        return render(request, 'Cards/no_access.html')
    return render(request, 'Cards/learn/learn.html', context)


@login_required
def write(request, set_id):
    folder = get_object_or_404(CardFolder, id=set_id)
    if folder.user != request.user:
        return render(request, 'Cards/no_access.html')
    langs = folder.get_langs()
    lang_keys = folder.get_langs(item='key')
    lang_full = folder.get_langs(item='value')
    length = len(langs)
    context = {
        'previous': False,
        'folder': folder,
        "length": length,
        "langs": langs,
        'width': 94 / length,
        'lang_full': lang_full,
        # 'previous_cards': List of previous cards,
        # 'm_card': Current multicard,
        # 'current_cards': Cards to display in this set,
    }

    if request.method == "POST":
        previous_multicard_id = int(request.POST['multicard_id'])
        context['previous'] = previous_multicard_id
        previous_multicard = MultiCard.objects.get(id=previous_multicard_id)
        previous_cards = []

        for lang, full_lang in langs:
            card = Card.objects.get(multi_card=previous_multicard, language=lang)
            previous_card = {
                'card': card,
                'language': full_lang.capitalize(),
                # 'answer': False or the answer
                # 'correct': If correct then True, else False
            }
            if card.show_answer:
                previous_card['answer'] = False
                card.check_show()
            else:
                answer = request.POST['answer' + card.language]
                # Calculating the points
                points = card.check_answer(answer)

                # Checking if user gave any input.
                if not answer:
                    previous_card['answer'] = 'No answer'
                else:
                    previous_card['answer'] = answer

                # If the answer is correct the points will be positive.
                if points > 0:
                    previous_card['correct'] = True
                else:
                    previous_card['correct'] = False
            previous_cards.append(previous_card)
        context['previous_cards'] = previous_cards

    # Get set of all the multicards from the folder and order them by priority, score.
    m_cards = MultiCard.objects.filter(cards_folder=folder, mastered=False).order_by('priority', 'score')

    # If it is not the first try, remove the previous multicard from the set to avoid repeat.
    if context['previous']:
        m_cards = m_cards.exclude(id=context['previous'])

    # Take first multicard from the ordered set and create a form from it.
    m_card = m_cards.first()
    if m_card is None:
        return render(request, 'Cards/learn/no_cards_to_learn.html', context)
        # TODO improve this template.

    # Create a list of cards in the order their language appear in the folder.
    current_cards = []
    any_answer_show = False
    for lang_key in lang_keys:
        card = Card.objects.get(multi_card=m_card, language=lang_key)
        current_cards.append(card)
        if card.show_answer:
            any_answer_show = True

    if not any_answer_show:
        show = rd.choice(current_cards)
        show.show_answer = True
        show.save()

    context['multicard_id'] = m_card.id
    context['current_cards'] = current_cards

    return render(request, 'Cards/learn/learn_write.html', context)


@login_required
def flashcards(request, set_id):
    folder = get_object_or_404(CardFolder, id=set_id)
    if folder.user != request.user:
        return render(request, 'Cards/no_access.html')
    length = len(folder.get_langs())
    lang_keys = folder.get_langs(item='key')
    lang_full = folder.get_langs(item='value')

    if length == 2:
        return flashcards_2(request, folder, lang_keys, lang_full)
    eles:
        return render(request, 'Cards/index.html')
    # elif length == 3:
    #     flashcards_3(request, folder, lang_keys, lang_full)
    # else:
    #     flashcards_4(request, folder, lang_keys, lang_full)


def flashcards_2(request, folder, lang_keys, lang_full):

    context = {
        'previous': False,
        'folder': folder,
        "lang_keys": lang_keys,
        'lang_full': lang_full,
        'reverse': False,
        'back_color': 'blue',
        'front_color': 'green',
        # front, back, mcard_id,
    }

    if request.method == "POST":
        previous_back = Card.objects.get(id=request.POST['card_id'])
        context['previous'] = previous_back
        progress = request.POST['progress']
        if progress == 'Delete this MultiCard':
            multicard = MultiCard.objects.get(id=request.POST['multicard_id'])
            multicard.delete()
        else:
            choices = {
                'Easily!': (40, 20),
                'Yes': (25, 12),
                'Barely': (8, 9),
                'Almost': (1, 6),
                'Nope': (-30, 2),
                'I have already mastered it!': (100, 100),
                'Reset my progress on this.': (-100, 1),
            }
            score_priority = choices[progress]
            previous_back.add_score_flashcards(score_priority)

    multicards = MultiCard.objects.filter(cards_folder=folder, mastered=False).order_by('priority', 'score')
    if context['previous']:
        multicards = multicards.exclude(id=request.POST['multicard_id'])
    multicard = multicards.first()
    if multicard is None:
        return render(request, 'Cards/learn/no_cards_to_learn.html', context)
    front = Card.objects.get(multi_card=multicard, language=lang_keys[0])
    back = Card.objects.get(multi_card=multicard, language=lang_keys[1])
    if front.score < back.score:
        front, back = back, front
        context["reverse"] = True
        context['back_color'] = 'green'
        context['front_color'] = 'blue'
    context['front'] = front
    context['back'] = back
    context['multicard_id'] = multicard.id
    return render(request, 'Cards/learn/learn_flashcards_2.html', context)



def flashcards_3(request, folder, lang_keys, lang_full):
    return render(request, 'Cards/learn/learn_flashcards_3.html', 'context')


def flashcards_4(request, folder, lang_keys, lang_full):
    return render(request, 'Cards/learn/learn_flashcards_4.html', 'context')

# https://3dtransforms.desandro.com/3d-transform-functions
# TODO add buttons to score
# TODO modify model function for scoring
