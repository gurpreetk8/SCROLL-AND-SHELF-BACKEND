from django.urls import path
from . import views

urlpatterns = [
    path('create_subscription/', views.create_subscription, name='create_subscription'),
    path('check_subscription/', views.check_subscription, name='check_subscription'),
]
