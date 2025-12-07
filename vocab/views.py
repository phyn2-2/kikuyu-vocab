from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q, Count, Prefetch
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.core.paginator import Paginator

from .models import Vocab, Category, Tag, Comment
from .forms import VocabForm, CommentForm

# ==========================================
# PUBLIC VIEWS (No Authentication Required)
# ==========================================

class VocabListView(ListView):
    model = Vocab
    template_name = 'vocab/vocab_list.html'
    context_object_name = 'vocabs'
    paginate_by = 20

    def get_queryset(self):
        """Returns filtered and searched vocabulary entries.
        Only shows approved words to public."""
        # Base query: only approved words
        queryset = Vocab.objects.filter(status='approved').select_related(
            'category',
            'user',
        ).prefetch_related(
            'tags'
        ).order_by('-created_at')

        # SEARCH functionality
        search_query = self.request.GET.get('q', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(word__icontains=search_query) |
                Q(translation__icontains=search_query) |
                Q(example_sentence__icontains=search_query) |
                Q(tags__name__icontains=search_query)
            ).distinct()    # distinct() prevents duplicates from tags

        # FILTER by category
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # FILTER by difficulty
        difficulty = self.request.GET.get('difficulty')
        if difficulty in ['beginner', 'intermediate', 'advanced']:
            queryset = queryset.filter(difficulty=difficulty)

        # FILTER by language
        language = self.request.GET.get('language')
        if language in ['kikuyu', 'english', 'swahili']:
            queryset = queryset.filter(language=language)

        # SORT options
        sort = self.request.GET.get('sort', '-created_at')
        if sort == 'popular':
            # Sort by view count
            queryset = queryset.order_by('-view_count')
        elif sort == 'alphabetical':
            queryset =queryset.order_by('word')
        elif sort == 'oldest':
            queryset = queryset.order_by('created_at')
        else:
            # Default: newest first
            queryset = queryset.order_by('created_at')

        return queryset

    def get_context_data(self, **kwargs):
        """Add extra data to template context."""
        context = super().get_context_data(**kwargs)

        # Categories for filter dropdown
        context['categories'] = Category.objects.annotate(
            word_count=Count('vocab_entries', filter=Q(vocab_entries__status='approved'))
        ).filter(word_count__gt=0)

        # Preserve search/filter state
        context['search_query'] = self.request.GET.get('q', '')
        context['active_category'] = self.request.GET.get('category', '')
        context['active_difficulty'] = self.request.GET.get('difficulty', '')
        context['active_language'] = self.request.GET.get('language','')
        context['active_sort'] = self.request.GET.get('sort','-created_at')

        # Statistics
        context['total_words'] = Vocab.objects.filter(status='approved').count()
        context['total_categories'] = Category.objects.count()

        # Check if user is authenticated for "Add Word" button
        context['can_contribute'] = self.request.user.is_authenticated

        return context

class VocabDetailView(DetailView):
    model = Vocab
    template_name = 'vocab/vocab_detail.html'

    def get_queryset(self):
        """Optimize query and handle permissions."""
        qs = Vocab.objects.select_related(
            'category',
            'user',
        ).prefetch_related(
            'tags',
            'comments__user',
            'favorites'
        )

        # If user is authenticated, let them see their own entries
        if self.request.user.is_authenticated:
            return qs.filter(
                Q(status='approved') | Q(user=self.request.user)
            )
        else:
            # Public: only approved
            return qs.filter(status='approved')

    def get_object(self):
        """Get the vocab entry and increment view counter.
        Only increment once per session to prevent spam."""
        obj = super().get_object()

        # Check if already viewed in this session
        viewed_key = f'viewed_vocab_{obj.pk}'
        if not self.request.session.get(viewed_key, False):
            obj.increment_view_count()
            self.request.session[viewed_key] = True
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vocab = self.object

        # Comments
        context['comments'] = vocab.comments.all()
        context['comment_form'] = CommentForm()

        # Check if current user favorited this
        if self.request.user.is_authenticated:
            context['is_favorited'] = vocab.favorites.filter(
                id=self.request.user.id
            ).exists()
        else:
            context['is_favorited'] = False

        # Related words (same category, excluding current)
        if vocab.category:
            context['related_words'] = Vocab.objects.filter(
                category=vocab.category,
                status='approved'
            ).exclude(
                pk=vocab.pk
            ).select_related('category')[:6]  # Show 6 related words
        else:
            context['related_words'] = []

        # Check if current user owns this entry (for edit button)
        context['is_owner'] = (
            self.request.user.is_authenticated and
            vocab.user == self.request.user
        )

        return context

# ============================================
# CONTRIBUTOR VIEWS (Authentication Required)
# ============================================

class VocabCreateView(LoginRequiredMixin, CreateView):
    """Add new vocubulary entry"""
    model = Vocab
    form_class = VocabForm
    template_name = 'vocab/vocab_form.html'

    def form_valid(self, form):
        """Set the contributor and inital status."""
        form.instance.user = self.request.user
        form.instance.status = 'pending'  # Always pending on submission

        messages.success(
            self.request,
            '✅ Word submitted successfully! It will appear after admin approval.'
        )

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Add New Word'
        context['submit_text'] = 'Submit for Review'
        return context

class VocabUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Edit existing vocubulary entry.
    Only the original contributor can edit, Editing resets status to 'pending' ( needs re-approval)"""
    model = Vocab
    form_class = VocabForm
    template_name = 'vocab/vocab_form.html'

    def test_func(self):
        """Check if current user owns this entry"""
        vocab = self.get_object()
        return vocab.user == self.request.user

    def form_valid(self, form):
        """Reset status to pending when edited"""
        # If word was rejected and now edited, reset to pending
        if self.object.status == 'rejected':
            form.instance.status = 'pending'
            form.instance.reviewed_by = None
            form.instance.reviewed_at = None
            form.instance.rejection_reason = ''

            messages.info(
                self.request,
                '📝 Changes submitted! Entry will be re-reviewed.'
            )
        else:
            messages.success(
                self.request,
                '✅ Word updated successfully!'
            )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Add context for template"""
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Edit Word'
        context['submit_text'] = 'Update Word'
        context['is_edit'] = True
        return context

class VocabDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete vocubulary entry.
    Only the original contributor can delete, deletes associated files (audio, image)"""

    model = Vocab
    template_name = 'vocab/vocab_confirm_delete.html'
    success_url = reverse_lazy('vocab-list')

    def test_func(self):
        vocab = self.get_object()
        return vocab.user == self.request.user

    def delete(self, request, *args, **kwargs):
        """Add success message on delete"""
        messages.success(
            self.request,
            '🗑️ Word deleted successfully.'
        )
        return super().delete(request, *args, **kwargs)

# =========================
# SOCIAL FEATURES
# =========================

@login_required
def favorite_vocab(request, pk):
    """Toggle favorite on a vocubulary entry.
    AJAX-friendly"""
    vocab = get_object_or_404(Vocab, pk=pk, status='approved')

    # Toggle favorite
    if request.user in vocab.favorites.all():
        vocab.favorites.remove(request.user)
        is_favorited = False
        message = 'Removed to favorites'
    else:
        vocab.favorites.add(request.user)
        is_favorited = True
        message = 'Added to favorites'

    # If AJAX request, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_favorited': is_favorited,
            'favorite_count': vocab.favorite_count(),
            'message': message
        })
    # Otherwise redirect back
    messages.success(request, f'❤️ {message} ')
    return redirect('vocab-detail', pk=pk)

@login_required
def add_comment(request, pk):
    """Add a comment to a vocubulary entry."""
    vocab = get_object_or_404(Vocab, pk=pk, status='approved')

    if request.method == 'POST':
        if form.is_valid():
            comment = form.save(commit=False)
            comment.vocab = vocab
            comment.user = request.user
            comment.save()

            messages.success(request, '💬 Comment added!')

        else:
            messages.error(request, '❌ Error adding comment.')

    return redirect('vocab-detail', pk=pk)

# =========================
# SEARCH & FILTER HELPERS
# =========================

def vocab_search(request):
    query = request.GET.get('q', '').strip()

    if not query:
        return redirect('vocab-list')

    # Search across multiple fields
    results = Vocab.objects.filter(
        Q(word__icontains=query) |
        Q(translation__icontains=query) |
        Q(example_sentence__icontains=query) |
        Q(tags__name__icontains=query),
        status='approved'
    ).distinct().select_related('category', 'user')

    context = {
        'vocabs': results,
        'search_query': query,
        'result_count': results.count(),
    }

    return render(request, 'vocab/vocab_search_results.html', context)

# =========================================
# USER DASHBOARD (Contributor's own words)
# =========================================

class MyVocabListView(LoginRequiredMixin, ListView):
    """Show current user's own vocubulary contributions.
    Includes pending, approved and rejected entries."""
    model = Vocab
    template_name = 'vocab/my_vocab_list.html'
    context_object_name = 'vocabs'
    paginate_by = 20

    def get_queryset(self):
        """Show only current user's entries"""
        return Vocab.objects.filter(
            user=self.request.user
        ).select_related('category').order_by('-created_at')

    def get_context_data(self, **kwargs):
        """Add Statistics about users's contributions"""
        context = super().get_context_data(**kwargs)
        user_vocabs = Vocab.objects.filter(user=self.request.user)

        context['stats'] = {
            'total': user_vocabs.count(),
            'pending': user_vocabs.filter(status='pending').count(),
            'approved': user_vocabs.filter(status='approved').count(),
            'rejected': user_vocabs.filter(status='rejected').count(),
        }

        return context

# ================
# CATEGORY BROWSE
# ================

class CategoryVocabListView(ListView):
    """Browse words by category"""
    model = Vocab
    template_name = 'vocab/category_vocab_list.html'
    context_object_name = 'vocabs'
    paginate_by = 20

    def get_queryset(self):
        """Filter by category slug"""
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Vocab.objects.filter(
            category=self.category,
            status='approved'
        ).select_related('user').order_by('-created_at')

    def get_context_data(self, **kwargs):
        """Add category info"""
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['word_count'] = self.get_queryset().count()
        return context
