from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

# Create your models here.

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.CharField(max_length=200, blank=True)    # eg "python,django,web"
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)

    class Meta:
        ordering = ['-published_date']    # newest first

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})

