from django.urls import path
from . import views
from .views import EventListView, EventDetailView, EventCreateView, EventUpdateView, EventDeleteView, EventListAll, UserListView



urlpatterns = [
    path('events/', EventListAll.as_view(), name='events-all'),
    path('invite-friends/<int:event_id>/', views.HtmlRender.invite_list, name="invite-list"),
    path('send-invite/', views.EventViews.invite_user, name="invite-user"),
    path('cancel-invite/', views.EventViews.cancel_invite, name="cancel-invite"),
    path('user/<str:username>', UserListView.as_view(), name='user-posts'),
    path('', views.HtmlRender.homePage, name='event-home'),
    path('event/<int:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('event/new/', EventCreateView.as_view(), name='event-create'),# Denne som gjør at vi kan aksessere events på event/1, pk er primary key for en post
    path('event/<int:pk>/update', EventUpdateView.as_view(), name='event-update'),
    path('event/<int:pk>/delete', EventDeleteView.as_view(), name='event-delete'),
    path('attendees/<int:event_id>/', views.HtmlRender.attendee_list, name="attendee-list"),
    path('remove-attendee/', views.EventViews.remove_attendee, name="remove-attendee"),
    path('add-host/', views.EventViews.add_host, name='add-host'),
    path('remove-host/', views.EventViews.remove_host, name='remove-host'),
    path('event/created/', views.HtmlRender.created_events, name='created-by-user'),
    path('handle-notification/<int:notification_id>', views.EventViews.redirect_notification, name="redirect-notification"),
    path('select-card/', views.EventViews.buy_ticket, name="buy-ticket"),
    path('to-transaction/<int:credit_id>', views.EventViews.redirect_to_execution, name='to-transaction'),
    path('execute-transaction', views.EventViews.execute_transaction, name="execute-transaction"),
    path('confirm-card/', views.EventViews.redirect_to_execution, name='select-card'),
    path('leave-waiting-list/', views.EventViews.leave_waiting_list, name='leave-waiting-list')
]
