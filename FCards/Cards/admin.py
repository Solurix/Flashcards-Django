from django.contrib import admin

from .models import CardFolder, MultiCard, Card


class CardInline(admin.TabularInline):
    model = Card
    extra = 5
    fieldsets = [
        (None, {'fields': ['language', 'main']}),
        ('Optional', {'fields': ['pronunciation', 'synonyms', 'definition', 'comment']})]


class MultiCardAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['cards_folder']}),
        ('Comment', {'fields': ['comment'], 'classes': ['collapse']})]
    inlines = [CardInline]
    list_display = ('comment', 'all_translations', 'max_languages')


class CardFolderAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['user', 'name', 'comment']}),
        ('Languages', {'fields': ['lang1', 'lang2', 'lang3', 'lang4', 'lang5']})]
    list_display = ('name', 'user', 'comment', "langs_no")


class CardAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['language', 'main']}),
        ('Optional', {'fields': ['pronunciation', 'synonyms', 'definition', 'comment']})]


admin.site.register(CardFolder, CardFolderAdmin)
admin.site.register(MultiCard, MultiCardAdmin)
# admin.site.register(Card, CardAdmin)
