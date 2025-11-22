from django.views.generic import ListView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.db import models  # ← ADDED THIS FOR Max, Case, When
import json

from .models import Task

class TaskListView(LoginRequiredMixin, ListView):
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'priority', 'due_date']
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        max_order = Task.objects.filter(user=self.request.user).aggregate(models.Max('order'))['order__max']
        form.instance.order = (max_order or -1) + 1
        return super().form_valid(form)

class TaskToggleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk, user=request.user)
        task.completed = not task.completed
        task.save()
        return JsonResponse({'completed': task.completed})

class TaskDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk, user=request.user)
        task.delete()
        return JsonResponse({'status': 'deleted'})

class TaskReorderView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body)
        order = data.get('order', [])
        Task.objects.filter(user=request.user, id__in=order).update(order=models.Case(
            *[models.When(id=id, then=pos) for pos, id in enumerate(order)],
            default='order',
            output_field=models.IntegerField()
        ))
        return JsonResponse({'status': 'success'})
