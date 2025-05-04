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

    path('get_series_books/', views.get_series_books, name='get_series_books'),
    path('get_all_series/', views.get_all_series, name='get_all_series'),

    path('get_book_reviews/', views.get_book_reviews, name='get_book_reviews'),
    path('submit_review/', views.submit_review, name='submit_review'),
    path('delete_review/', views.delete_review, name='delete_review'),
    path('get_user_review/', views.get_user_review, name='get_user_review'),

    path('add_to_wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('get_wishlist/', views.get_wishlist, name='get_wishlist'),
    path('remove_from_wishlist/', views.remove_from_wishlist, name='remove_from_wishlist'),

    path('add_reading_book/', views.add_reading_book, name='add_reading_book'),
    path('get_reading_books/', views.get_reading_books, name='get_reading_books'),

    path('recommend_books/', views.recommend_books, name='recommend_books'),
    
    
]