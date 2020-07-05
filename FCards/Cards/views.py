from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import FolderForm, CardsForm
from .multithreads import *
from threading import Thread


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
    if folder.user != request.user:
        return render(request, 'Cards/no_access.html')

    if request.method == 'POST':
        form = FolderForm(request.POST or None, instance=folder)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.save()
            t = Thread(target=edit_folder_translate, args=[folder])
            t.setDaemon(False)
            t.start()
            return render(request, 'Cards/index.html')

    else:
        form = FolderForm(instance=folder)
    return render(request, 'Cards/edit_set.html', {'form': form})


@login_required
def view_folder(request, set_id):
    folder = get_object_or_404(CardFolder, id=set_id)
    if folder.user != request.user:
        return render(request, 'Cards/no_access.html')
    return render(request, 'Cards/view_set.html', {'folder': folder})


@login_required
def add_multicard(request, set_id):
    folder = get_object_or_404(CardFolder, id=set_id)
    if folder.user != request.user:
        return render(request, 'Cards/no_access.html')

    langs = folder.get_langs(item='key')
    form = CardsForm(request.POST or None)
    context = {
        "form": form,
        'folder': folder,
        "length": len(langs),
        "langs": folder.get_langs(),
    }
    if request.method == "POST":
        if request.POST['main' + langs[0]]:
            m_card = MultiCard.objects.create(cards_folder=folder, comment=request.POST['comment'],
                                              definition=request.POST['definition'])
            m_card.save()
            t = Thread(target=add_multicard_translate, args=[langs, request, m_card, folder])
            t.setDaemon(False)
            t.start()
        return redirect(request.META['HTTP_REFERER'])

    return render(request, 'Cards/add_multicard.html', context)


@login_required
def add_many(request, set_id):
    folder = get_object_or_404(CardFolder, id=set_id)
    if folder.user != request.user:
        return render(request, 'Cards/no_access.html')
    langs = folder.get_langs()
    length = len(langs)
    form = CardsForm(request.POST or None)
    context = {
        "form": form,
        'folder': folder,
        "length": length,
        "langs": langs,
    }
    if request.method == "POST":
        separator = str(request.POST['separator'])
        language = str(request.POST['language'])
        for_translate = request.POST['for_translate']

        # If user messes with the validations (all below three are required).
        if not separator or not language or not for_translate:
            return render(request, 'Cards/no_access.html')

        new_cards = for_translate.split(separator)
        new_langs = folder.get_langs(item='key')

        # Get all the languages except the source.
        new_langs.remove(language)

        for word in new_cards:
            m_card = MultiCard.objects.create(cards_folder=folder)
            m_card.save()
            word = word.capitalize()
            Card.objects.create(multi_card=m_card, cards_folder=folder, language=language, main=word, synonyms="",
                                comment="", pronunciation="")

            t = Thread(target=add_many_translate, args=[new_langs, word, language, m_card, folder])
            t.setDaemon(False)
            t.start()
        return redirect(request.META['HTTP_REFERER'])

    return render(request, 'Cards/add_many.html', context)


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

# TODO If words are too long they need to be wrapped. Otherwise they are breaking the tables.
# TODO count folders by occurrence in that user folders
# TODO [play.html] add auto-focus and ability to go next on enter even if no input required
# TODO [play.html] add comments, hints
# TODO footer
