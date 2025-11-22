from django.urls import path
from . import views

urlpatterns = [
    path('', views.VocabListView.as_view(), name='vocab-list'),
    path('new/', views.VocabCreateView.as_view(), name='vocab-create'),
    path('<int:pk>/', views.VocabDetailView.as_view(), name='vocab-detail'),
    path('<int:pk>/edit/', views.VocabUpdateView.as_view(), name='vocab-edit'),
    path('<int:pk>/delete/', views.VocabDeleteView.as_view(), name='vocab-delete'),
    path('<int:pk>/favorite/', views.favorite_vocab, name='vocab-favorite'),
    path('<int:pk>/comment/', views.add_comment, name='add-comment'),
    path('search/', views.vocab_search, name='vocab-search')
]

