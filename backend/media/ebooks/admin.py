from traceback import format_tb
from django.contrib import admin

from backend.ebooks.models import ReviewRating,Series, SeriesImage
from .models import Series,Ebook, Category, SampleImage

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

class SeriesImageInline(admin.TabularInline):  # or StackedInline
    model = SeriesImage
    extra = 1
    fields = ('image', 'caption', 'uploaded_at')
    readonly_fields = ('uploaded_at',)

class SeriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'book_count', 'created_at')
    search_fields = ('name',)
    inlines = [SeriesImageInline]  # Use the new inline here
    
    def book_count(self, obj):
        return obj.books.count()

class EbookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'book_type', 'series_info', 'created_at', 'categories')
    search_fields = ('title', 'author', 'description')
    list_filter = ('created_at', 'book_type', 'series', 'category')  # Added category to filters
    ordering = ('-created_at',)
    inlines = [SampleImageInline]

    def categories(self, obj):
        return ', '.join([c.name for c in obj.category.all()])  # Changed to category (singular as per your ForeignKey)
    
    def series_info(self, obj):
        if obj.series:
            return f"{obj.series.name} (#{obj.series_order})"
        return "Standalone"
    
class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'ebook_title', 'rating_stars', 'review_preview', 'created_at', 'updated_at')
    list_filter = ('rating', 'created_at', 'ebook')
    search_fields = ('user__email', 'user__first_name', 'user__last_name','ebook__title','review_text')
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
        return format_tb(
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