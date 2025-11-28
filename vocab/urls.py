from django.urls import path
from . import views

urlpatterns = [
    # Public Browse
    path('', views.VocabListView.as_view(), name='vocab-list'),
    path('search/', views.vocab_search, name='vocab-search'),
    path('category/<slug:slug>/', views.CategoryVocabListView.as_view(), name='vocab-category'),

    # Detail View
    path('<int:pk>/', views.VocabDetailView.as_view(), name='vocab-detail'),

    # Contributor Actions (Login Required)
    path('new/', views.VocabCreateView.as_view(), name='vocab-create'),
    path('<int:pk>/edit/', views.VocabUpdateView.as_view(), name='vocab-edit'),
    path('<int:pk>/delete/', views.VocabDeleteView.as_view(), name='vocab-delete'),
    path('my-words/', views.MyVocabListView.as_view(), name='my-vocab'),

    # Social Features
    path('<int:pk>/favorite/', views.favorite_vocab, name='vocab-favorite'),
    path('<int:pk>/comment/', views.add_comment, name='add-comment'),
]
