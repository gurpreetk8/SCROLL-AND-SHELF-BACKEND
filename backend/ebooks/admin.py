from django.contrib import admin
from .models import Ebook, Category, SampleImage, RequestBook, ReviewRating, Series, SeriesImage

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
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
    readonly_fields = ('uploaded_at',)
    verbose_name = 'Series Image'
    verbose_name_plural = 'Series Images'

class EbookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at',)
    search_fields = ('title', 'author', 'description')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    inlines = [SampleImageInline]

    def categories(self, obj):
        return ', '.join([c.name for c in obj.categories.all()])

class SeriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    inlines = [SeriesImageInline]

class RequestBookAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'author', 'genre', 'created_at')
    list_filter = ('genre', 'created_at')
    search_fields = ('title', 'author', 'genre', 'user__email')
    ordering = ('-created_at',)
    readonly_fields = ('user', 'title', 'author', 'genre', 'message', 'created_at')

    def has_add_permission(self, request):
        # Disable manual adding from admin
        return False
    
class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'ebook_title', 'rating', 'short_review', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__email', 'ebook__title', 'review_text')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user', 'ebook')  # Better for performance with many users/ebooks

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'

    def ebook_title(self, obj):
        return obj.ebook.title
    ebook_title.short_description = 'Ebook Title'
    ebook_title.admin_order_field = 'ebook__title'

    def short_review(self, obj):
        if obj.review_text:
            return f"{obj.review_text[:50]}..." if len(obj.review_text) > 50 else obj.review_text
        return "-"
    short_review.short_description = 'Review Excerpt'

    def get_fields(self, request, obj=None):
        fields = ['user', 'ebook', 'rating', 'review_text', 'created_at', 'updated_at']
        if obj:  # Editing an existing object
            return fields
        return ['user', 'ebook', 'rating', 'review_text']  # Creating new - exclude readonly

    def has_add_permission(self, request):
        # Optional: prevent adding reviews directly in admin if they should only come from users
        return True  # Set to False if you want to disable adding via admin

admin.site.register(Category, CategoryAdmin)
admin.site.register(Ebook, EbookAdmin)
admin.site.register(RequestBook, RequestBookAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(ReviewRating, ReviewRatingAdmin)