from django.contrib import admin
from .models import Task
# Register your models here.

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'priority', 'completed', 'due_date', 'created_at')
    list_filter = ('priority', 'completed', 'user')
    search_fields = ('title',)

