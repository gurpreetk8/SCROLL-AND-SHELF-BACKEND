from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to="ebooks/category_images/", default="ebooks/category_images/default.png")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Ebook(models.Model):
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