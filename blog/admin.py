from django.contrib import admin
from .models import Post
from django.utils import timezone

# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_date', 'was_published_recently')
    list_filter = ('published_date', 'author')
    search_fields = ('title', 'content')
    prepopulated_fields = {'tags': ('title',)}    # auto-fill tags from title

    def was_published_recently(self, obj):
        return obj.published_date >= timezone.now() - timezone.timedelta(days=7)
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Recent?'
