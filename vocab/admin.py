from django.contrib import admin
from .models import Vocab, Tag, Comment

# Register your models here.

@admin.register(Vocab)
class VocabAdmin(admin.ModelAdmin):
    list_display = ('word', 'language', 'user', 'created_at')
    list_filter = ('language', 'user')
    search_fields = ('word', 'translation')
    filter_horizontal = ('tags','favorites')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('vocab', 'user', 'created_at')


