from django.contrib import admin

from backend.ebooks.models import Series, SeriesImage
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


admin.site.register(Category, CategoryAdmin)
admin.site.register(Ebook, EbookAdmin)
admin.site.register(Series, SeriesAdmin)