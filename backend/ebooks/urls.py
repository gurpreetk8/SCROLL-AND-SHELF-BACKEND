from django.urls import path
from ebooks import views

urlpatterns = [
    path('all_ebooks/', views.get_all_ebooks, name='get_all_ebooks'),
    path('latest_ebooks/', views.get_latest_ebooks, name='get_latest_ebooks'),
    path('all_categories/', views.get_all_categories, name='get_all_categories'),

    path('ebook_detail/', views.get_ebook_detail, name='get_ebook_detail'),
    path('best_sellers/', views.get_best_sellers, name='get_best_sellers'),
    path('trending_books/', views.get_trending_books, name='get_trending_books'),
    path('best_of_month_book/', views.get_best_of_the_month_book, name='get_best_of_the_month_book'),
    path('ebooks_by_category/', views.get_ebooks_by_category, name='get_ebooks_by_category'),

    path('add_to_wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('get_wishlist/', views.get_wishlist, name='get_wishlist'),
    path('remove_from_wishlist/', views.remove_from_wishlist, name='remove_from_wishlist'),
]