from django.shortcuts import render, get_object_or_404

# Create your views here.

from django.http import HttpResponse
from django.template import loader
from .models import CardFolder, MultiCard, Card


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


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
