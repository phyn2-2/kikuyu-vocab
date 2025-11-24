from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import FileExtensionValidator
from django.utils.text import slugify
import os

class Category(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Category name (e.g., 'Noun', 'Verb')"
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        blank=True,
        help_text="URL-friendly version (auto-generated)"
    )
    description = models.TextField(
        blank=True,
        help_text="Brief description of this category"
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Emoji or icon for UI display"
    )

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_word_count(self):
        return self.vocab_entries.filter(status='approved').count()

class Tag(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Vocab(models.Model):
    # Language choices
    LANGUAGE_CHOICES = [
        ('kikuyu', 'Kikuyu'),
        ('english', 'English'),
        ('swahili', 'Swahili'),
    ]

    # Approval workflow statuses
    STATUS_CHOICES = [
        ('pending', '⏳ Pending Review'),
        ('approved', '✅ Approved'),
        ('rejected', '❌ Rejected'),
    ]

    # Difficulty levels for learners
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    # === Core Fields ===
    word = models.CharField(
        max_length=100,
        db_index=True,    # Index for faster searches
        help_text="The word in its native language"
    )

    translation = models.CharField(
        max_length=100,
        db_index=True,
        help_text="English translation"
    )

    language = models.CharField(
        max_length=20,
        choices=LANGUAGE_CHOICES,
        default='kikuyu',
        db_index=True
    )

    # === Categorization ===
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vocab_entries',
        help_text="Primary category (Noun, Verb, etc.)"
    )

    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='vocab_entries',
        help_text="Contextual tags (food, family, travel, etc.)"
    )

    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='beginner',
        help_text="Difficulty level for learners"
    )

    # === Rich Content ===
    example_sentence = models.TextField(
        blank=True,
        help_text="Example sentence using this word (in native language)"
    )

    example_translation = models.TextField(
        blank=True,
        help_text="English translation of example sentence"
    )

    pronunciation_guide = models.CharField(
        max_length=200,
        blank=True,
        help_text="Written pronunciation guide (e.g., 'moo-n-doo')"
    )

    notes = models.TextField(
        blank=True,
        help_text="Additional notes, context, or cultural info"
    )

    # === Media Files ===
    audio = models.FileField(
        upload_to='vocab_audio/%Y/%m',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['mp3', 'wav' ,'ogg', 'm4a']
            )
        ],
        help_text="Audio pronunciation (MP3, WAV, OGG, M4A)"
    )

    image = models.ImageField(
        upload_to='vocab_images/%Y/%m',
        blank=True,
        null=True,
        help_text="Visual context (optional)"
    )

    # === Approval Workflow ===
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
        help_text="Approval status (pending/approved/rejected)"
    )

    rejection_reason = models.TextField(
        blank=True,
        help_text="Admin notes on why entry was rejected"
    )

    # === User Tracking ===
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='vocabs',
        help_text="User who contributed this word"
    )

    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_vocabs',
        help_text="Admin who approved/rejected this entry"
    )

    # === Social Features ===
    favorites = models.ManyToManyField(
        User,
        related_name='favorite_vocabs',
        blank=True,
        help_text="Users who favorited this word"
    )

    view_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this word was viewed"
    )

    # === Timestamps ===
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this entry was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last modification time"
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When admin reviewed this entry"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Vocabulary Entry"
        verbose_name_plural = "Vocabulary Entries"
        # Prevent duplicate words in the same language
        unique_together = [['word', 'language']]

        # Database indexes for performance
        indexes = [
            models.Index(fields=['status', 'language']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['word', 'translation']),
        ]

    def __str__(self):
        return f"{self.word} ({self.get_language_display()}) -> {self.translation}"
    def get_absolute_url(self):
        return reverse('vocab-detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        # if updating and audio/image changed, delete old files
        if self.pk:
            try:
                old = Vocab.objects.get(pk=self.pk)

                # Delete old audio if new one uploaded
                if old.audio and old.audio != self.audio:
                    if os.path.isfile(old.audio.path):
                        os.remove(old.audio.path)

                # Delete old image if new one uploaded
                if old.image and old.image != self.image:
                    if os.path.isfile(old.image.path):
                        os.remove(old.image.path)
            except Vocab.DoesNotExist:
                pass

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete audio file
        if self.audio and os.path.isfile(self.audio.path):
            os.remove(self.audio.path)

        # Delete image file
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)

        super().delete(*args, **kwargs)

    # === Helper Methods ===
    def is_approved(self):
        """Check if entry is approved"""
        return self.status == 'approved'

    def is_pending(self):
        """Check if entry is pending review"""
        return self.status == 'pending'

    def is_rejected(self):
        """Check if entry was rejected"""
        return self.status == 'rejected'

    def favorite_count(self):
        """Returns number of users who favorited this word"""
        return self.comments.count()

    def comment_count(self):
        """Returns number of comments on this word"""
        return self.comments.count()

    def increment_view_count(self):
        """Increment view counter (call when word is viewed)"""
        self.view_count += 1
        self.save(update_fields=['view_count'])

    def has_audio(self):
        """Check if audio file exists"""
        return bool(self.audio)

    def has_image(self):
        """Check if image exists"""
        return bool(self.image)

    def get_status_badge(self):
        """Returns HTML badge for status (for templates)"""
        badges = {
            'pending': '<span class="badge badge-warning">⏳ Pending</span>',
            'approved': '<span class="badge badge-success">✅ Approved</span>',
            'rejected': '<span class="badge badge-danger">❌ Rejected</span>',
        }
        return badges.get(self.status, '')

class Comment(models.Model):
    vocab = models.ForeignKey(
        Vocab,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="The vocab entry this comment belongs to"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="User who wrote this comment"
    )

    content = models.TextField(
        help_text="Comment text"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # Moderation (if needed)
    is_flagged = models.BooleanField(
        default=False,
        help_text="Flagged for review by moderators"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comment by {self.user.username} on {self.vocab.word}"

    def get_short_content(self, length=50):
        """Returns truncated comment content"""
        if len(self.content) > length:
            return f"{self.content[:length]}..."
        return self.content

class LearningProgress(models.Model):
    """Track user learning progress (Future Feature not in MVP)
    for now it's just a placeholder structure"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='learner_progress'
    )

    vocab = models.ForeignKey(
        Vocab,
        on_delete=models.CASCADE,
        related_name='learner_progress'
    )

    MASTERY_CHOICES = [
        ('new','New'),
        ('learning', 'Learning'),
        ('practiced', 'Practiced'),
        ('mastered', 'Mastered'),
    ]

    mastery_level = models.CharField(
        max_length=20,
        choices=MASTERY_CHOICES,
        default='new'
    )

    times_reviewed = models.PositiveIntegerField(default=0)
    last_reviewed = models.DateTimeField(null=True, blank=True)
    next_review = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user','vocab'],
                name='unique_user_vocabulary'
            )
        ]
        verbose_name = "Learning Progress"
        verbose_name_plural = "Learning Progress"

    def __str__(self):
        return f"{self.user.username} - {self.vocab.word} ({self.mastery_level})"














