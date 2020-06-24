from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader
from django.forms import formset_factory
from .models import CardFolder, MultiCard, Card
from .forms import FolderForm, CardsForm
from googletrans import Translator


def detail(request, set_id):
    this_set = CardFolder.objects.get(pk=set_id)  # Current set
    multicards = this_set.multicard_set.all()  # All multicards in the set

    print(multicards)
    context = {
        "set": this_set,
        "multicards": multicards,
    }
    return render(request, 'Cards/sets.html', context)


def results(request, set_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % set_id)


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
        print('else')
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
                        if not lang in created_langs:
                            first = cards.first()
                            translation = Translator().translate(text=first.main, src=first.language, dest=lang)
                            data = {}
                            data['main'] = translation.text
                            if translation.pronunciation != first.main:
                                data['pronunciation'] = translation.pronunciation
                                data['automated'] = True
                            Card.objects.create(multi_card=multicard, language=lang, **data)
                return render(request, 'Cards/index.html')

        else:
            form = FolderForm(instance=folder)
        return render(request, 'Cards/edit_set.html', {'form': form})
    else:
        return render(request, 'Cards/no_access.html')


# @login_required
# def add_multicard(request, set_id):
#     folder = get_object_or_404(CardFolder, id=set_id)
#     length = len(folder.get_langs())
#     # MultiCardSet = inlineformset_factory(MultiCard, Card, fields=('main',), extra=length)
#     CardsFormSet = formset_factory(CardsForm, can_delete=False, extra=length)
#     data = {
#         'form-TOTAL_FORMS': str(length),
#         'form-INITIAL_FORMS': '0',
#         'form-MAX_NUM_FORMS': '',
#     }
#     if request.method == "POST":
#         formset = CardsFormSet(queryset=)
#         cleaned_form = formset.cleaned_data
#         print(formset.errors)
#         print(formset)
#         print(cleaned_form)
#         if formset.is_valid():
#             if request.method == "POST":
#                 cleaned_form = formset.cleaned_data
#                 print(cleaned_form)
#                 # CardFolder.objects.create(user=request.user, **form.cleaned_data)
#                 return render(request, 'Cards/index.html')
#
#     context = {
#         "formset": formset,
#         'folder': folder,
#         "length": length,
#     }
#     return render(request, 'Cards/add_multicard.html', context)

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
                MCard = MultiCard.objects.create(cards_folder=folder)
                MCard.save()
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
                    Card.objects.create(multi_card=MCard, language=k, **data[k])
            return render(request, 'Cards/index.html')
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
                return render(request, 'Cards/no_access.html')  # TODO easter egg
            new_cards = for_translate.split(separator)
            new_langs = folder.langs_keys()
            print(new_langs)
            new_langs.remove(language)
            print(new_langs)
            for word in new_cards:
                MCard = MultiCard.objects.create(cards_folder=folder)
                MCard.save()
                Card.objects.create(multi_card=MCard, language=language, main=word)
                for lang in new_langs:
                    translation = Translator().translate(text=word, src=language, dest=lang)
                    data = {}
                    data['main'] = translation.text.capitalize
                    data['language'] = lang
                    data['synonyms'] = ""
                    data['comment'] = ""
                    data['pronunciation'] = ""
                    if translation.pronunciation != word:
                        data['pronunciation'] = translation.pronunciation.capitalize
                        data['automated'] = True
                    else:
                        data['pronunciation'] = ""
                        data['automated'] = False
                    Card.objects.create(multi_card=MCard, **data)

            return render(request, 'Cards/index.html')
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
    user_folders = request.user.cardfolder_set.all()
    langs = folder.get_langs()
    length = len(langs)
    context = {
        # "form": form,
        'folder': folder,
        "length": length,
        "langs": langs,
    }
    return render(request, 'Cards/edit_multicards.html', context)
