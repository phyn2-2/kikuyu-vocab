from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Q
from django.contrib import messages
from django.utils import timezone
from .models import Vocab, Category, Tag, Comment, LearningProgress

# =================================
# INLINE ADMINS (Related Objects)
# =================================

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0  # Don't show empty forms
    readonly_fields = ['user', 'created_at', 'content']
    can_delete = True

    fields = ['user', 'content', 'created_at', 'is_flagged']

    def has_add_permission(self, request, obj=None):
        """Prevent adding comments from admin (users add via frontend)"""
        return False

# ===============
# CATEGORY ADMIN
# ===============

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Manage word categories (Noun, Verb, etc.)"""
    list_display = ['name', 'icon', 'word_count_display', 'slug']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

    fieldset = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'icon')
        }),
        ('Details', {
            'fields': ('description',),
            'classes': ('collapse',)  # Collapsible section
        }),
    )

    def word_count_display(self, obj):
        """Shows count of approved words in this category"""
        count = obj.get_word_count()
        color = '#b5cf6' if count > 0 else '#6b7280'
        return format_html(
            '<span style="color: {}; font-weight: 600;">{} words</span>',
            color,
            count
        )
    word_count_display.short_description = 'Word Count'

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

# ==========
# TAG ADMIN
# ==========

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Manage contextual tags (food, family, travel, etc)"""
    list_display = ['name', 'slug', 'usage_count', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']

    def usage_count(self, obj):
        """Shows how many vocab entries use this tag"""
        count = obj.vocab_entries.filter(status='approved').count()
        return f"{count} entries"
    usage_count.short_description = 'Used In'

# ===============
# COMMENT ADMIN
# ===============

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Moderate user comments"""
    list_display = ['vocab_link', 'user', 'short_content', 'created_at', 'is_flagged']
    list_filter = ['is_flagged', 'created_at']
    search_fields = ['content', 'user__username', 'vocab__word']
    readonly_fields = ['created_at'] #*

    date_hierarchy = 'created_at'

    def vocab_link(self,obj):
        """Clickable link to the vocab entry"""
        url = reverse('admin:vocab_vocab_change', args=[obj.vocab.pk])
        return format_html('<a href="{}">{}</a>', url, obj.vocab.word)
    vocab_link.short_description = 'Vocab Entry'

    def short_content(self, obj):
        """Truncated comment preview"""
        return obj.get_short_content(60)
    short_content.short_description = 'Comment'

    actions = ['flag_comments', 'unflag_comments']

    def flag_comments(self, request, queryset):
        """Bulk flag comments for review"""
        update = queryset.update(is_flagged=True)
        self.message_user(request, f'{updated} comment(s) flagged.', messages.WARNING)
    flag_comments.short_description = "🚩 Flag selected comments"

    def unflag_comments(self, request, queryset):
        """Bulk unflag comments"""
        updated = queryset.update(is_flagged=False)
        self.message_user(request, f'{updated} comment(s) unflagged.', messages.SUCCESS)
    unflag_comments.short_description = "✅ Unflag selected comments"

# ============================
# VOCAB ADMIN (THE MAIN ONE)
# ============================
@admin.register(Vocab)
class VocabAdmin(admin.ModelAdmin):

    class Media:
        css = {
            'all': ('vocab/admin_enhance',)
        }

    # === LIST VIEW ===
    list_display = [
        'word_display',
        'translation',
        'language_badge',
        'category',
        'status_badge',
        'media_preview',
        'contributor',
        'stats_display',
        'created_at',
    ]

    list_filter = [
        'status',
        'language',
        'difficulty',
        'category',
        'created_at',
        ('reviewed_by', admin.EmptyFieldListFilter),  # Filter by reviewed/not reviewed
    ]

    search_fields = [
        'word',
        'translation',
        'example_sentence',
        'user__username',
        'tags__name',
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
        'reviewed_at',
        'reviewed_by',
        'view_count',
        'audio_player',
        'image_preview',
        'contributor_info',
        'favorite_count_display',
    ]

    # Pre-fill category field with search
    autocomplete_fields = ['tags']

    # Horizontal filter
    filter_horizontal = ['tags', 'favorites']

    # Date drill-down navigation
    date_hierarchy = 'created_at'

    # Pagination
    list_per_page = 25

    # === FIELDSETS (Organize edit page) ===
    fieldsets = (
        ('📝 Word Information', {
            'fields': (
                ('word', 'translation'),
                ('language', 'category', 'difficulty'),
                'pronunciation_guide',
            )
        }),
        ('💬 Examples & Context', {
            'fields': (
                'example_sentence',
                'example_translation',
                'notes',
            ),
            'classes': ('collapse',),  # Collapsible section
        }),
        ('🎵 Media Files', {
            'fields': (
                'audio',
                'audio_player',  # Readonly preview
                'image',
                'image_preview',  # Readonly preview
            ),
        }),
        ('🏷️ Classification', {
            'fields': ('tags',),
        }),
        ('✅ Approval Workflow', {
            'fields': (
                'status',
                'rejection_reason',
                'reviewed_by',
                'reviewed_at',
            ),
            'classes': ('collapse',),
        }),
        ('👤 Contributor', {
            'fields': (
                'contributor_info',
                'user',
            ),
            'classes': ('collapse'),
        }),
        ('📊 Analytics', {
            'fields': (
                'view_count',
                'favorite_count_display',
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
        ('❤️ Social', {
            'fields': ('favorites',),
            'classes': ('collapse'),
        }),
    )

    # === INLINE MODELS ===
    inlines = [CommentInline]

    # === CUSTOM DISPLAY METHODS ===

    def word_display(self, obj):
        """Styled word display with emphasis"""
        return format_html(
            '<strong style="color: #8b5cf6; font-size: 16px;">{}</strong>',
            obj.word
        )
    word_display.short_description = 'Word'

    def language_badge(self, obj):
        """Color-coded language badge"""
        colors = {
            'kikuyu': '#b5cf6',  # Purple
            'english': '#3b82f6',  # Blue
            'swahili': '#10b981',  # Green
        }
        color = colors.get(obj.language, '#6b7280')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-size: 11px; font-weight: 600; '
            'text-transform: uppercase;">{}</span>',
            color,
            obj.get_language_display()
        )
    language_badge.short_description = 'Language'

    def status_badge(self, obj):
        """Visual status indicator with emoji"""
        badges = {
            'pending': ('<span style="background: #f59e0b; color: white;">', '⏳ Pending'),
            'approved': ('<span style="background: #10b981; color: white;">', '✅ Approved'),
            'rejected': ('<span style="background: #ef4444; color: white;">', '❌ Rejected'),
        }
        badge_html, badge_text = badges.get(obj.status, ('<span>', obj.status))
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; '
            'border-radius: 4px; font-size: 11px; font-weight: 600; '
            'text-transform: uppercase;">{}</span>',
            badge_html,
            badge_text
        )
    status_badge.short_description = 'Status'

    def media_preview(self, obj):
        """Quick preview of audio/image availability"""
        icons = []
        if obj.audio:
            icons.append('🎵')
        if obj.image:
            icons.append('🖼️')
        return ' '.join(icons) if icons else '--'
    media_preview.short_description = 'Media'

    def contributor(self, obj):
        """Link to contributor's profile"""
        url = reverse('admin:auth_user_change', args=[obj.user.pk])
        return format_html(
            '<a href="{}" style="color: #8b5cf6;">{}</a>',
            url,
            obj.user.username
        )
    contributor.short_description = 'Contributor'

    def stats_display(self, obj):
        """Shows views and favorites count"""
        return format_html(
            '<span style="color: #6b7280; font-size: 12px;">👁️{} | ❤️ {}</span>',
            obj.view_count,
            obj.favorite_count()
        )
    stats_display.short_description = 'Stats'

    def audio_player(self, obj):
        """Inline audio player for quick preview"""
        if obj.audio:
            return format_html(
                '<audio controls style="width: 100%; max-width: 400px;">'
                '<source src="{}" type="audio/mpeg">'
                'Your browser does not support audio playback.'
                '</audio>',
                obj.audio.url
            )
        return format_html('<span style="color: #9ca3af;">No audio uploaded</span>')
    audio_player.short_description = 'Audio Preview'

    def image_preview(self, obj):
        """Inline image thumbnail"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px; '
                'border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);" />',
                obj.image.url
            )
        return format_html('<span style="color: #9ca3af;">No image uploaded</span>')
    image_preview.short_description = 'Image Preview'

    def contributor_info(self, obj):
        """Detailed contributor Information"""
        total_contributions = Vocab.objects.filter(user=obj.user).count()
        approved = Vocab.objects.filter(user=obj.user, status='approved').count()

        return format_html(
            '<div style="padding: 10px; background: #1e1e2e; border-radius: 6px; '
            'border-left: 3px solid #8b5cf6;">'
            '<p style="margin: 0; color: #e0e7ff;"><strong>{}</strong></p>'
            '<p style="margin: 5px 0 0 0; color: #a5b4fc; font-size: 12px;">'
            'Total: {} entries | Approved: {} entries'
            '</p></div>',
            obj.user.get_full_name() or obj.user.username,
            total_contributions,
            approved
        )
    contributor_info.short_description = 'Contributor Details'

    def favorite_count_display(self, obj):
        """Shows who favorited this word"""
        count = obj.favorite_count()
        if count == 0:
            return "No favorites yet"
        return f"{count} user(s) favorited this"
    favorite_count_display.short_description = 'Favorites'

    # === CUSTOM ACTIONS ===

    actions = [
        'approve_entries',
        'reject_entries',
        'mark_pending',
        'delete_selected_with_files',
    ]

    def approve_entries(self, request, queryset):
        """Bulk approve multiple entries at once.
        Sets status to 'approved' and records who approved it."""
        updated = queryset.update(
            status='approved',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(
            request,
            f'✅ Successfully approved {updated} entry/entries.',
            messages.SUCCESS
        )
    approve_entries.short_description= "✅ Approve selected entries"

    def reject_entries(self, request, queryset):
        """
        Bulk reject entries.
        Manually add rejection reasons in edit page.
        """
        updated = queryset.update(
            status='rejected',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(
            request,
            f'❌ Rejected {updated} entry/entries. Add rejection reasons in edit page.',
            messages.WARNING
        )
    reject_entries.short_description = f"❌ Reject selected entries"

    def mark_pending(self, request, queryset):
        """Reset status to pending (if you want to re-review)"""
        updated = queryset.update(
            status='pending',
            reviewed_by=None,
            reviewed_at=None,
            rejection_reason=''
        )
        self.message_user(
            request,
            f'⏳ Marked {updated} entry/entries as pending review.',
            messages.INFO
        )
    mark_pending.short_description = "⏳ Mark as pending review"

    def delete_selected_with_files(self, request, queryset):
        """Delete entries AND their associated files.
        Better than default delete which might leave orphaned files"""
        count = queryset.count()
        for obj in queryset:
            obj.delete()  # Triggers custom delete() method in model

        self.message_user(
            request,
            f'🗑️ Deleted {count} entry/entries and associated files.',
            messages.SUCCESS
        )
    delete_selected_with_files.short_description = "🗑️ Delete selected(with files)"

    # === SAVE OVERRIDE ===

    def save_model(self, request, obj, form, change):
        """Override save to automatically set reviewed_by when status changes."""
        if change:  # If editing existing object
            original = Vocab.objects.get(pk=obj.pk)

            # If Status changed and no reviewed_by set, set it to current user
            if original.status != obj.status and not obj.reviewed_by:
                obj.reviewed_by = request.user
                obj.reviewed_at = timezone.now()

        super().save_model(request, obj, form, change)

    # === CUSTOM QUERYSET ===

    def get_queryset(self, request):
        """Optimize queries by pre-fetching related objects.
        Prevents N+1 query problem (important for performance)."""
        qs = super().get_queryset(request)
        return qs.select_related(
            'user',
            'category',
            'reviewed_by'
        ).prefetch_related(
            'tags',
            'favorites',
            'comments'
        )
# =========================================
# LEARNING PROGRESS ADMIN (Future Feature)
# =========================================

@admin.register(LearningProgress)
class LearningProgressAdmin(admin.ModelAdmin):
    """Track user learning progress (Phase 2 feature).
    For now, just basic admin to see data."""
    list_display = ['user', 'vocab', 'mastery_level', 'times_reviewed', 'last_reviewed']
    list_filter = ['mastery_level', 'user']
    search_fields = ['user__username', 'vocab__word']
    readonly_fields = ['times_reviewed', 'last_reviewed', 'next_review']

    def has_add_permission(self, request):
        """Prevent manual creation (auto-generated by system)"""
        return False











