from django import forms
from django.core.exceptions import ValidationError
from .models import Vocab, Comment, Tag
import os

class VocabForm(forms.ModelForm):
    # Custom tag input (comma-separated)
    tag_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'family, food, greetings(comma-separated)',
            'class': 'form-control'
        }),
        help_text='Add tags separated by commas (e.g., family, food, travel)'
    )
    class Meta:
        model = Vocab
        fields = [
            'word',
            'translation',
            'language',
            'category',
            'difficulty',
            'pronunciation_guide',
            'example_sentence',
            'example_translation',
            'notes',
            'audio',
            'image',
        ]

        widgets = {
            'word': forms.TextInput(attrs={
                'placeholder': 'Enter Kikuyu word',
                'class': 'form-control',
                'autofocus':True
            }),
            'translation': forms.TextInput(attrs={
                'placeholder': 'English translation',
                'class': 'form-control'
            }),
            'language': forms.Select(attrs={
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'difficulty': forms.Select(attrs={
                'class': 'form-control'
            }),
            'pronunciation_guide': forms.TextInput(attrs={
                'placeholder': 'e.g., "moo-n-doo" (optional)',
                'class': 'form-control'
            }),
            'example_sentence': forms.Textarea(attrs={
                'placeholder': 'Example sentence in Kikuyu (optional)',
                'class': 'form-control',
                'rows':3
            }),
            'example_translation': forms.Textarea(attrs={
                'placeholder': 'English translation of example (optional)',
                'class': 'form-control',
                'rows': 3
            }),
            'notes': forms.Textarea(attrs={
                'placeholder': 'Additional context or cultural notes (optional)',
                'class': 'form-control',
                'rows': 3
            }),
            'audio': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'audio/*'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }

        help_text = {
            'word': 'The word in its native language',
            'translation': 'English meaning',
            'audio': 'MP3, WAV, or WEBP (max 5mb)',
            'category': 'Choose the grammatical category',
            'difficulty': 'How difficult is this word for learners',
        }

        labels = {
            'word': 'Kikuyu word *',
            'translation': 'English Translation *',
            'language': 'Language *',
            'difficulty': 'Difficulty level',
            'pronunciation_guide': 'Pronunciation Guide',
            'example_sentence': 'Example Sentence',
            'example_translation': 'Example Translation',
            'notes': 'Additional Notes',
            'audio': 'Audio Pronunciation',
            'image': 'Visual Context',
        }

    def __init__(self, *args, **kwargs):
        """Initialize form and populate tag field if editing."""
        super().__init__(*args, **kwargs)

        # If editing existing entry, populate tags
        if self.instance.pk:
            tags = self.instance.tags.all()
            self.fields['tag_input'].initial = ', '.join(
                [tag.name for tag in tags]
            )

    def clean_audio(self):
        """Validate audio file.Checks file size (max 10mb) and file extension"""
        audio = self.cleaned_data.get('audio')

        if audio:
            # Check file size (10mb = 10 * 1024 * 1024 bytes)
            if audio.size > 10 * 1024 * 1024:
                raise ValidationError('Audio file too large. Max size is 10mb.')

            # Check file extension
            ext = os.path.splitext(audio.name)[1].lower()
            valid_extensions = ['.mp3', '.wav', '.ogg', '.m4a']
            if ext not in valid_extensions:
                raise ValidationError(
                    f'Invalid audio format. Allowed: {", ".join(valid_extensions)}'
                )
        return audio

    def clean_image(self):
        image = self.cleaned_data.get('image')

        if image:
            # Check file size (5mb)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('Image file too large. Max size is 5mb')

            # Check file extension
            ext = os.path.splitext(image.name)[1].lower()
            valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
            if ext not in valid_extensions:
                raise ValidationError(
                    f'Invalid image format. Allowed: {", ".join(valid_extensions)}'
                )
        return image

    def clean(self):
        """Cross-field validation.Ensures if example_sentence provided, example_translation should be too"""
        cleaned_data = super().clean()
        example_sentence = cleaned_data.get('example_sentence')
        example_translation = cleaned_data.get('example_translation')

        if example_sentence and not example_translation:
            self.add_error(
                'example_translation',
                'Please provide English translation of the example.'
            )
        return cleaned_data

    def save(self, commit=True):
        """Save vocab entry and handle tags"""
        instance = super().save(commit=commit)

        if commit:
            # Clear existing tags
            instance.tags.clear()

            # Process tag input
            tag_input = self.cleaned_data.get('tag_input', '')
            if tag_input:
                tag_names = [
                    tag.strip().lower()
                    for tag in tag_input.split(',')
                    if tag.strip()
                ]

                for tag_name in tag_names:
                    # Get or create tag
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    instance.tags.add(tag)

        return instance

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': 'Share your thoughts, ask questions, or add context...',
                'class': 'form-control',
                'rows':3
            })
        }

        labels = {
            'content': 'Your Comment'
        }

    def clean_content(self):
        """Validate comment content"""
        content = self.cleaned_data.get('content', '').strip()

        if len(content) < 3:
            raise ValidationError('Comment too short.Minimum 3 characters.')

        if len(content) > 1000:
            raise ValidationError('Comment too long.Maximum 1000 characters.')

        return content


