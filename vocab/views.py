from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from .models import Vocab, Comment
from .forms import VocabForm, CommentForm

# Create your views here.
class VocabListView(LoginRequiredMixin, ListView):
    model = Vocab
    template_name = 'vocab/vocab_list.html'
    context_object_name = 'vocabs'
    paginate_by = 20

    def get_queryset(self):
        return Vocab.objects.filter(user=self.request.user)
class VocabDetailView(LoginRequiredMixin, DetailView):
    model = Vocab
    template_name = 'vocab/vocab_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()
        context['form'] = CommentForm()
        return context

class VocabCreateView(LoginRequiredMixin, CreateView):
    model = Vocab
    form_class = VocabForm
    template_name = 'vocab/vocab_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class VocabUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Vocab
    form_class = VocabForm
    template_name = 'vocab/vocab_form.html'

    def test_func(self):
        return self.get_object().user == self.request.user

class VocabDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Vocab
    success_url = '/vocab/'
    template_name = 'vocab/vocab_confirm_delete.html'

    def test_func(self):
        return self.get_object().user == self.request.user

def favorite_vocab(request, pk):
    vocab = get_object_or_404(Vocab, pk=pk)
    if request.user in vocab.favorites.all():
        vocab.favorites.remove(request.user)
    else:
        vocab.favorites.add(request.user)
    return redirect('vocab-detail', pk=pk)

def add_comment(request, pk):
    vocab = get_object_or_404(Vocab, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.vocab = vocab
            comment.user = request.user
            comment.save()
    return redirect('vocab-detail', pk=pk)

def vocab_search(request):
    query = request.GET.get('q')
    results = Vocab.objects.filter(user=request.user)
    if query:
        results = results.filter(Q(word__icontains=query) | Q(translation__icontains=query) | Q(example_sentence__icontains=query))
    return render(request, 'vocab/vocab_list.html', {'vocabs': results})


