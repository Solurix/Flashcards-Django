from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import FolderForm, CardsForm
from .multithreads import *
from threading import Thread
from .models import CardFolder, MultiCard


@login_required
def home(request):
    return redirect('/')


def demo_welcome(request):
    form = FolderForm(request.POST or None)
    context = {
        "folder_form": form
    }
    return render(request, 'Cards/demo/welcome.html', context)


# region Folder

@login_required
def delete_folder(request, set_id):
    if request.method == 'POST':
        folder = CardFolder.objects.get(id=set_id)
        folder.delete()
        return redirect('/')
    else:
        return redirect('/')


@login_required
def add_folder(request):
    form = FolderForm(request.POST or None)
    if form.is_valid():
        if request.method == "POST":
            folder = CardFolder.objects.create(user=request.user, **form.cleaned_data)
            enough = len(folder.multicard_set.all()) > 2
            return render(request, 'Cards/view_set.html', {'folder': folder, 'enough': enough})

    context = {
        "form": form
    }
    return render(request, 'Cards/add_set.html', context)


@login_required
def edit_folder(request, set_id):
    folder = get_object_or_404(CardFolder, id=set_id)
    if folder.user != request.user:
        return redirect('/no_access/')
    if folder.being_edited:
        return render(request, 'Cards/folder_being_updated.html', {'folder': folder})

    if request.method == 'POST':
        form = FolderForm(request.POST or None, instance=folder)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.being_edited = True
            folder.save()
            t = Thread(target=edit_folder_translate, args=[folder])
            t.setDaemon(False)
            t.start()
            enough = len(folder.multicard_set.all()) > 2
            return render(request, 'Cards/view_set.html', {'folder': folder, 'enough': enough})

    else:
        form = FolderForm(instance=folder)
    return render(request, 'Cards/edit_set.html', {'form': form, 'folder': folder})


@login_required
def copy_folder(request, set_id):
    folder = get_object_or_404(CardFolder, id=set_id)
    if request.method == 'POST':
        form = FolderForm(request.POST or None, instance=folder)
        if form.is_valid():
            new_folder = CardFolder.objects.get(id=set_id)
            new_folder.pk = None
            new_folder.id = None
            new_folder.user = request.user
            new_folder.public = False
            new_folder.save()
            for multicard in folder.multicard_set.all():
                new_multicard = MultiCard.objects.get(id=multicard.id)
                new_multicard.id = None
                new_multicard.pk = None
                new_multicard.mastered = False
                new_multicard.score = 0
                new_multicard.priority = 0
                new_multicard.cards_folder = new_folder
                new_multicard.save()
                for card in multicard.card_set.all():
                    new_card = card
                    new_card.pk = None
                    new_card.id = None
                    new_card.mastered = False
                    new_card.score = 0
                    new_card.priority = 0
                    new_card.multi_card = new_multicard
                    new_card.cards_folder = new_folder
                    new_card.save()
            form = FolderForm(request.POST or None, instance=new_folder)
            new_folder = form.save(commit=False)
            new_folder.being_edited = True
            new_folder.save()
            t = Thread(target=edit_folder_translate, args=[new_folder])
            t.setDaemon(False)
            t.start()
            # return redirect('Cards/view_set.html', {'folder': new_folder})
            return redirect(f'/cards/view_set/{new_folder.id}/')

    else:
        form = FolderForm(instance=folder)
    return render(request, 'Cards/copy_set.html', {'form': form})


@login_required
def view_folder(request, set_id):
    folder = get_object_or_404(CardFolder, id=set_id)
    enough = len(folder.multicard_set.all()) > 2
    for card in folder.card_set.all():
        if card.pronunciation == 'False' or (card.pronunciation == card.main):
            card.pronunciation = ''
            card.save()
    if folder.user != request.user:
        return redirect('/no_access/')
    return render(request, 'Cards/view_set.html', {'folder': folder, 'enough': enough})


@login_required
def reset_progress(request, set_id):
    folder = get_object_or_404(CardFolder, id=set_id)
    if folder.user != request.user:
        return redirect('/no_access/')
    MultiCard.objects.filter(cards_folder=folder).update(priority=10, score=0)
    Card.objects.filter(cards_folder=folder).update(priority=1, score=0)
    return redirect(request.META['HTTP_REFERER'])


# endregion

# region MultiCards

@login_required
def add_multicard(request, set_id):
    folder = get_object_or_404(CardFolder, id=set_id)
    if folder.user != request.user:
        return redirect('/no_access/')

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
        # return redirect(f'/cards/add_multicard/{folder.id}/')
        return redirect(f'/cards/view_set/{folder.id}/')
    return render(request, 'Cards/add_multicard.html', context)


@login_required
def add_many(request, set_id):
    folder = get_object_or_404(CardFolder, id=set_id)
    if folder.user != request.user:
        return redirect('/no_access/')
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
        if not language or not for_translate:
            return redirect('/no_access/')

        if not separator:
            separator = " "
        new_cards = for_translate.split(separator)
        new_langs = folder.get_langs(item='key')

        # Get all the languages except the source.
        new_langs.remove(language)

        for word in new_cards:
            if word == "" or word == "　":
                continue
            word = word.strip(" ,　")
            m_card = MultiCard.objects.create(cards_folder=folder)
            m_card.save()
            word = word.capitalize()
            Card.objects.create(multi_card=m_card, cards_folder=folder, language=language, main=word, synonyms="",
                                comment="", pronunciation="")

            t = Thread(target=add_many_translate, args=[new_langs, word, language, m_card, folder])
            t.setDaemon(False)
            t.start()
        return redirect(f'/cards/view_set/{folder.id}/')

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
        return redirect('/no_access/')


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
            return redirect('/no_access/')
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
        return redirect('/no_access/')


# endregion

# region Public

@login_required
def make_public(request, set_id):
    folder = get_object_or_404(CardFolder, id=set_id)
    if folder.user != request.user:
        return redirect('/no_access/')
    if folder.public:
        folder.public = False
    else:
        folder.public = True
    folder.save()
    return redirect(request.META['HTTP_REFERER'])


@login_required
def view_folder_public(request, set_id):
    folder = get_object_or_404(CardFolder, id=set_id)
    return render(request, 'Cards/view_set_public.html', {'folder': folder})


@login_required
def public_sets(request):
    folders = CardFolder.objects.filter(public=True)
    return render(request, 'Cards/public_sets.html', {'folders': folders})


# endregion

# region Other

@login_required
def refresh_update(request, set_id):
    folder = get_object_or_404(CardFolder, id=set_id)
    if folder.user != request.user:
        return redirect('/no_access/')
    clean_errors(folder)
    updates = MultiCard.objects.filter(being_edited=True, cards_folder=folder)
    if updates or folder.being_edited:
        return render(request, 'Cards/folder_being_updated.html', {'folder': folder})
    else:
        return edit_folder(request, folder.id)


@login_required
def repair_translations(request, set_id):
    folder = get_object_or_404(CardFolder, id=set_id)
    if folder.user != request.user:
        return redirect('/no_access/')
    clean_errors(folder)
    t = Thread(target=repair_translations_thread, args=[folder])
    t.setDaemon(False)
    t.start()
    # TODO add message that translations are in work
    return redirect(f'/cards/view_set/{folder.id}/')

# endregion

# TODO If words are too long they need to be wrapped. Otherwise they are breaking the tables.
# TODO count folders by occurrence in that user folders
# TODO [learn_write.html] add auto-focus and ability to go next on enter even if no input required
# TODO [learn_write.html] add comments, hints, message-at least 2 cards are required
