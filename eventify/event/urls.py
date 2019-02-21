from django.urls import path
from . import views



urlpatterns = [
    path('', views.HtmlRender.home, name='eventify-home'),
    path('about/', views.HtmlRender.about, name='eventify-about'),
]
