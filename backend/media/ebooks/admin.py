from django.contrib import admin
from .models import Ebook, Category, SampleImage

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

class EbookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at',)
    search_fields = ('title', 'author', 'description')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    inlines = [SampleImageInline]

    def categories(self, obj):
        return ', '.join([c.name for c in obj.categories.all()])

admin.site.register(Category, CategoryAdmin)
admin.site.register(Ebook, EbookAdmin)