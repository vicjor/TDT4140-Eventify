from django.urls import path
from . import views



urlpatterns = [
    path('', views.home, name='eventify-home'),
    path('about/', views.about, name='eventify-about')
]
