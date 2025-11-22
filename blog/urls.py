from django.urls import path
from . import views

urlpatterns = [
    path('', views.PostListView.as_view(), name='post-list'),
    path('post/<int:pk>', views.PostDetailView.as_view(), name='post-detail'),
    path('post/new/', views.PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post-edit'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post-delete'),
]

