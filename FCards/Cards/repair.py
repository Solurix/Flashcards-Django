from .models import CardFolder, MultiCard, Card


def capitalize_strip_all_words():
    x = 0
    attribute_errors = []
    for card in Card.objects.all():
        try:
            card.main = card.main.strip().capitalize()
            if card.pronunciation:
                card.pronunciation = card.strip().pronunciation.capitalize()
            if card.synonyms:
                card.synonyms = card.synonyms.strip().capitalize()
            if card.comment:
                card.comment = card.comment.strip().capitalize()
            card.save()
            x += 1
        except AttributeError:
            attribute_errors.append((card.id, card.language))

    print('Attribute error in %d cards (id, lang):' % len(attribute_errors), attribute_errors)
    print('Capitalized %d cards!' % x)
