from django.urls import path
from . import views

urlpatterns = [
    path('', views.TaskListView.as_view(), name='task-list'),
    path('add/', views.TaskCreateView.as_view(), name='task-add'),
    path('<int:pk>/toggle/', views.TaskToggleView.as_view(), name='task-toggle'),
    path('<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task-delete'),
    path('reorder/', views.TaskReorderView.as_view(), name='task-reorder'),
]


