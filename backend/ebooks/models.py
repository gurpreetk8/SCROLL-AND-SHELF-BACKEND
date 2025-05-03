from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator  # Add this line
from django.core.exceptions import ValidationError  # Also needed for clean()


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

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

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

    # ✅ Add ManyToManyField here:
    tags = models.ManyToManyField(Tag, related_name='ebooks', blank=True)

    def __str__(self):
        return self.title
    
class Wishlist(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    ebook = models.ForeignKey(Ebook, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class ReviewRating(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    ebook = models.ForeignKey(Ebook, on_delete=models.CASCADE, related_name='reviews_ratings')
    
    # Rating (required if review exists, but can also exist alone)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], 
        null=True,  # Optional if user only wants to review (but we'll enforce via clean())
        blank=True
    )
    
    # Review (optional)
    review_text = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'ebook']  # One rating/review per user per book
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.ebook.title} ({self.rating or 'No rating'})"

    def clean(self):
        """
        Ensure:
        1. If review_text exists, rating must exist.
        2. At least one of rating or review_text must exist.
        """
        if self.review_text and not self.rating:
            raise ValidationError("A rating is required when submitting a review.")
        if not self.rating and not self.review_text:
            raise ValidationError("Either a rating or review must be provided.")
    
    def save(self, *args, **kwargs):
        self.full_clean()  # Enforce validation on save
        super().save(*args, **kwargs)

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