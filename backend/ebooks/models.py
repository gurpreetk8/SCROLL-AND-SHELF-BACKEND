from django.db import models

class Category(models.Model):
    TYPE_CHOICES = [
        ('fiction', 'Fiction'),
        ('non-fiction', 'Non-Fiction'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to="ebooks/category_images/", blank=True, null=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='fiction')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Series(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="series/covers/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Ebook(models.Model):
    BOOK_TYPE_CHOICES = [
        ('standalone', 'Standalone'),
        ('series', 'Series'),
    ]
    book_type = models.CharField(
        max_length=20,
        choices=BOOK_TYPE_CHOICES,
        default='standalone'
    )
    series = models.ForeignKey(
        Series,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='books'
    )
    series_order = models.PositiveIntegerField(null=True, blank=True)

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    description = models.TextField()
    cover_image = models.ImageField(upload_to="ebooks/covers/")
    file = models.FileField(upload_to="ebooks/files/")
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='ebooks')
    best_seller = models.BooleanField(default=False)
    best_of_month = models.BooleanField(default=False)
    trending = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Wishlist(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    ebook = models.ForeignKey(Ebook, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class SampleImage(models.Model):
    ebook = models.ForeignKey(Ebook, on_delete=models.CASCADE, related_name='sample_images')
    image = models.ImageField(upload_to="ebooks/samples/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ebook.title} sample #{self.id}"
    
class SeriesImage(models.Model):
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='series_images')
    image = models.ImageField(upload_to="series/sample_images/")
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.series.name} image #{self.id}"