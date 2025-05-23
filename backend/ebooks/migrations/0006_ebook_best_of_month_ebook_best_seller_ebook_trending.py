# Generated by Django 5.2 on 2025-04-30 06:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ebooks', '0005_category_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebook',
            name='best_of_month',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='ebook',
            name='best_seller',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='ebook',
            name='trending',
            field=models.BooleanField(default=False),
        ),
    ]
