"""eventify URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from users import views as user_views
from event import views as event_views
from django.conf import settings
from django.conf.urls.static import static

# path(URL-pattern (ex. 'admin/' -> localhost:8000/admin/), method to whom you
urlpatterns = [
    path('admin/', admin.site.urls),
    path('get-cards/', user_views.get_credit_cards, name="get-cards"),
    path('register/', user_views.register, name="register"),
    path('profile/', user_views.profile, name="profile"),
    path('edit-profile/', user_views.editProfile, name="edit-profile"),
    path('my-events/', event_views.HtmlRender.myEvents, name='my-events'),
    path('all-events/', event_views.HtmlRender.allEvents, name='all-events'),
    path('events/search/', event_views.EventViews.search_events, name='event-search'),
    path('event/join/', event_views.EventViews.eventJoin, name='event-join'),
    path('event/leave/', event_views.EventViews.leaveEvent, name='event-leave'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name="login"),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name="logout"),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), name="password_reset"),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name="password_reset_done"),
    path('password-reset-confirm/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name="password_reset_confirm"),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name="password_reset_complete"),
    path('all-users/', user_views.get_users, name="all-users"),
    path('add-friend/', user_views.add_contact, name="add-contact"),
    path('accept-friend/', user_views.accept_request, name="accept-request"),
    path('decline-friend/', user_views.decline_request, name="decline-request"),
    path('cancel-request/', user_views.cancel_request, name="cancel-request"),
    path('requests/', user_views.see_requests, name="contact-requests"),
    path('contacts/', user_views.get_friends, name="contacts"),
    path('remove-contact/', user_views.remove_contact, name="remove-contact"),
    path('user-search/', user_views.search_user, name='user-search'),
    path('user-search-event/', user_views.search_user_event, name='user-search-event'),
    path('invites/', user_views.event_invites, name='event-invites'),
    path('decline-invite/', event_views.EventViews.event_decline_from_invitation, name='event-decline-from-invitation'),
    path('register-card/', user_views.register_credit, name='register-card'),
    path('', include('event.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
