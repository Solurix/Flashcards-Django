from ..models import Card
from django import template
from ..langcodes import LangCodesDict

register = template.Library()


@register.simple_tag
def get_card(lang, multicard):
    try:
        mcard = Card.objects.get(language=lang, multi_card=multicard)
    except Card.DoesNotExist:
        mcard = None
    return mcard


@register.filter
def get_lang(key):
    return LangCodesDict.get(key)


@register.filter
def index(sequence, position):
    return sequence[position]


@register.filter
def width(languages):
    length = len(languages)
    return 94 / length

