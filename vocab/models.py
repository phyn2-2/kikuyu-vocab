from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.
class Vocab(models.Model):
    LANGUAGE_CHOICES = [
        ('kikuyu', 'Kikuyu'),
        ('english', 'English'),
        ('swahili', 'Swahili'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vocabs')
    word = models.CharField(max_length=100)
    translation = models.CharField(max_length=100)
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='kikuyu')
    example_sentence = models.TextField(blank=True)
    audio = models.FileField(upload_to='vocab_audio/', blank=True, null=True)
    image = models.ImageField(upload_to='vocab_images/', blank=True, null=True)
    tags = models.ManyToManyField('Tag', blank=True)
    favorites = models.ManyToManyField(User, related_name='favorite_vocabs', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.word} ({self.language})"

    def get_absolute_url(self):
        return reverse('vocab-detail', kwargs={'pk': self.pk})

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Comment(models.Model):
    vocab = models.ForeignKey(Vocab, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


