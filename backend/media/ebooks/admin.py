from traceback import format_tb
from django.contrib import admin
from django.utils.html import format_html
from backend.ebooks.models import ReviewRating, Series, SeriesImage, UserBook
from .models import Series, Ebook, Category, SampleImage, ReviewRating,UserBook

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'created_at')
    list_filter = ('type',)
    search_fields = ('name',)
    ordering = ('name',)

class SampleImageInline(admin.TabularInline):
    model = SampleImage
    extra = 1
    readonly_fields = ('uploaded_at',)
    verbose_name = 'Sample Image'
    verbose_name_plural = 'Sample Images'

class SeriesImageInline(admin.TabularInline):
    model = SeriesImage
    extra = 1
    fields = ('image', 'caption', 'uploaded_at')
    readonly_fields = ('uploaded_at',)

class SeriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'book_count', 'created_at')
    search_fields = ('name',)
    inlines = [SeriesImageInline]
    
    def book_count(self, obj):
        return obj.books.count()

class UserBookAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'book_title', 'status_badge', 'reading_duration', 'last_read')
    list_filter = ('status', 'started_reading')
    search_fields = ('user__email', 'book__title')
    readonly_fields = ('started_reading', 'last_read', 'created_at')
    date_hierarchy = 'last_read'
    list_per_page = 20
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def book_title(self, obj):
        return obj.book.title
    book_title.short_description = 'Book'
    book_title.admin_order_field = 'book__title'
    
    def status_badge(self, obj):
        color = {
            'reading': 'green',
            'completed': 'blue',
            'paused': 'orange'
        }.get(obj.status, 'gray')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 2px 6px; border-radius: 10px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def reading_duration(self, obj):
        if obj.status == 'completed':
            duration = obj.last_read - obj.started_reading
            return f"{duration.days} days" if duration.days > 0 else "<1 day"
        return "In progress"
    reading_duration.short_description = 'Duration'

class EbookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'book_type', 'display_tags', 'series_info', 'series_order', 'created_at', 'categories', 'reading_count')
    search_fields = ('title', 'author', 'description', 'tags')
    list_filter = ('created_at', 'book_type', 'series', 'category')
    ordering = ('-created_at',)
    inlines = [SampleImageInline]

    def categories(self, obj):
        return ', '.join([c.name for c in obj.category.all()])
    
    def series_info(self, obj):
        if obj.series:
            return f"{obj.series.name} (#{obj.series_order})"
        return "Standalone"
    
    def display_tags(self, obj):
        return ", ".join(obj.get_tags_list())
    display_tags.short_description = 'Tags'
    
    def reading_count(self, obj):
        count = obj.userbook_set.filter(status='reading').count()
        return format_html(
            '<a href="/admin/ebooks/userbook/?book__id__exact={}">{}</a>',
            obj.id,
            f"{count} reading" if count else "-"
        )
    reading_count.short_description = 'Readers'
    
class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'ebook_title', 'rating_stars', 'review_preview', 'created_at', 'updated_at')
    list_filter = ('rating', 'created_at', 'ebook')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'ebook__title', 'review_text')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Relations', {
            'fields': ('user', 'ebook')
        }),
        ('Review Content', {
            'fields': ('rating', 'review_text')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'

    def ebook_title(self, obj):
        return obj.ebook.title
    ebook_title.short_description = 'Ebook'
    ebook_title.admin_order_field = 'ebook__title'

    def rating_stars(self, obj):
        if not obj.rating:
            return "No rating"
        return format_html(
            '<span style="color: #f39c12;">{}</span>', 
            '★' * obj.rating + '☆' * (5 - obj.rating)
        )
    rating_stars.short_description = 'Rating'

    def review_preview(self, obj):
        if not obj.review_text:
            return "-"
        preview = obj.review_text[:50]
        if len(obj.review_text) > 50:
            preview += "..."
        return preview
    review_preview.short_description = 'Review Preview'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'ebook')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Ebook, EbookAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(ReviewRating, ReviewRatingAdmin)
admin.site.register(UserBook, UserBookAdmin)