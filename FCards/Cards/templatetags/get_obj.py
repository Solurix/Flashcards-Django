from django import template

register = template.Library()
from ..models import Card


@register.simple_tag
def get_card(lang, multicard):
    try:
        mcard = Card.objects.get(language=lang, multi_card=multicard)
    except Card.DoesNotExist:
        mcard = None
    return mcard
