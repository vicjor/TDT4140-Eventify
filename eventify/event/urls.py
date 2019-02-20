from django.urls import path
from . import views



urlpatterns = [
    path('', views.HtmlRender.home, name='eventify-home'),
    path('about/', views.HtmlRender.about, name='eventify-about'),
    path('createEvent/', views.HtmlRender.createEvent, name='create-event'),
    path('allEvents/', views.HtmlRender.allEvents, name='all-events'),
    path('myEvents/', views.HtmlRender.myEvents, name='my-events'),
    path('editEvent/', views.HtmlRender.editEvent, name='edit-event'),
    path('event/update/<int:post_id>/', views.EventViews.updateEvent, name='update-event'),
    path('event/remove/', views.EventViews.removeEvent, name='remove-event'),
    path('event/create/', views.EventViews.createEvent, name='createEvent'),
    path('event/search/', views.EventViews.searchEvents, name='searchEvents'),
    path('event/details/', views.EventViews.eventDetails, name='eventDetails'),
    path('event/join/', views.EventViews.eventJoin, name='eventJoin'),
]
