from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader

from .models import CardFolder, MultiCard, Card
from .forms import FolderForm


# def index(request):
#     return HttpResponse("Hello, world. You're at the polls index.")


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
def home(request):
    return render(request, 'Cards/index.html')

@login_required
def delete_folder(request, set_id):
    if request.method == 'POST':
        Folder = CardFolder.objects.get(id=set_id)
        Folder.delete()
        return render(request, 'Cards/index.html')
    else:
        print('else')
        return render(request, 'Cards/index.html')

@login_required
def edit_folder(request, set_id):
    Folder = CardFolder.objects.get(id=set_id)
    form = FolderForm(request.POST or None, instance=Folder)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            # if request.method == "POST":
            #     CardFolder.objects.create(user=request.user, **form.cleaned_data)
        return render(request, 'Cards/index.html')

    context = {
        "form": form
    }
    return render(request, 'Cards/edit_set.html', context)