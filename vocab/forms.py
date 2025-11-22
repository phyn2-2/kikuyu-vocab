from django import forms
from .models import Vocab, Tag, Comment

class VocabForm(forms.ModelForm):
    tags = forms.CharField(required=False, help_text='Comma separated, e.g. greetings, food', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'greetings, food,animals...'}))

    class Meta:
        model = Vocab
        fields = ['word', 'translation', 'language', 'example_sentence', 'audio', 'image']
        widgets ={
            'word': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the word...'}),
            'translation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter translation...'}),
            'language': forms.Select(attrs={'class': 'form-select'}),
            'example_sentence': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add an example sentence...'}),
            'audio': forms.FileInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            tag_names = [t.strip() for t in self.cleaned_data['tags'].split(',') if t.strip()]
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                instance.tags.add(tag)
        return instance

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add your comment...'})}


