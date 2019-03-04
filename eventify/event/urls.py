from django.urls import path
from . import views
from .views import EventListView, EventDetailView, EventCreateView, EventUpdateView, EventDeleteView



urlpatterns = [
    path('events/', views.HtmlRender.home, name='events-all'),
    path('', EventListView.as_view(), name='event-home'),
    path('event/<int:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('event/new/', EventCreateView.as_view(), name='event-create'),#Denne som gjør at vi kan aksessere events på event/1, pk er primary key for en post
    path('event/<int:pk>/update', EventUpdateView.as_view(), name='event-update'),
    path('event/<int:pk>/delete', EventDeleteView.as_view(), name='event-delete'),
    path('about/', views.HtmlRender.about, name='eventify-about'),
    path('event/created/', views.HtmlRender.created_events, name='created-by-user')
]
