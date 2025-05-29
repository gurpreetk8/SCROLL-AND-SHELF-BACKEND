from django.contrib import admin
from .models import Ebook, Category, SampleImage, RequestBook

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

class EbookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at',)
    search_fields = ('title', 'author', 'description')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    inlines = [SampleImageInline]

    def categories(self, obj):
        return ', '.join([c.name for c in obj.categories.all()])

class RequestBookAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'author', 'genre', 'created_at')
    list_filter = ('genre', 'created_at')
    search_fields = ('title', 'author', 'genre', 'user__email')
    ordering = ('-created_at',)
    readonly_fields = ('user', 'title', 'author', 'genre', 'message', 'created_at')

    def has_add_permission(self, request):
        # Disable manual adding from admin
        return False

admin.site.register(Category, CategoryAdmin)
admin.site.register(Ebook, EbookAdmin)
admin.site.register(RequestBook, RequestBookAdmin)