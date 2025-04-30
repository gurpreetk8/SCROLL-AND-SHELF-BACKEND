from django.urls import path
from . import views

urlpatterns = [
    path('pre_book_subscription/', views.pre_book_subscription, name='pre_book_subscription'),
]
