from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.contrib.sessions import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Post
from users.models import Notification, Credit
from django.contrib import messages
from django.db.models import F
from django.utils import timezone
import pytz
import json
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm
from django.core.mail import send_mail, send_mass_mail
import os
from django.conf import settings

events = [
]


def handle_upload(request):
    """
    Functionality for updating an already existing profile. Checks that all user input is valid and executes the update.
    If the input is invalid relevant error messages are displayed.
    :param request: An HTTP request from user containing input.
    :return: Redirects the user to the profile page.
    """
    if request.method == 'POST':
        p_form = UploadFileForm(request.POST,
                                request.FILES,
                                instance=request.user.profile)
        if p_form.is_valid():
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')

    else:
        p_form = UploadFileForm(instance=request.user.profile)

    context = {
        'p_form': p_form
    }
    return render(request, 'users/profile.html', context)


class EventListView(ListView):
    """
    Class for displaying the events ordered by the date the events are starting.
    """
    model = Post
    template_name = 'event/home.html'
    context_object_name = 'events'
    ordering = ['-start_date']

    def get_queryset(self):
        """
        Filters all events such that the private events are excluded and sorts them by date.
        :return: A list where all private events are excluded.
        """
        return Post.objects.filter(is_private=False).order_by('-start_date')


class UserListView(ListView):
    """
    Class for displaying all the events creating by a specific user.
    """
    model = Post
    template_name = 'event/user_posts.html' #<app>/<model>_<viewtype>.html
    context_object_name = 'events'

    def get_queryset(self):
        """
        Filters out all the events created by the user with "username"
        :return: The list of all events created by a specific user sorted by the date they were posted.
        """
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')
    paginate_by = 6


class EventListAll(ListView):
    """
    Class for displaying the events ordered by the date the events are starting.
    """
    model = Post
    template_name = 'event/all_events.html'
    context_object_name = 'events'
    ordering = ['-date_posted']

    def get_queryset(self):
        """
        Exclude all private events and excludes the ones written by the user requesting.
        :return: The list with all events that's not private or written by the requesting user.
        """
        events = Post.objects.filter(is_private=False).order_by('-date_posted')
        try:
            events.exclude(author=self)
        except TypeError:
            pass
        return events
    paginate_by = 6


class EventDetailView(DetailView):
    model = Post
    template_name = 'event/event_detail.html'
    context_object_name = 'events'


class EventCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = [
        'title',
        'location',
        'content',
        'price',
        'attendance_limit',
        'waiting_list_limit',
        'start_date',
        'end_date',
        'image',
        'is_private'
    ]
    template_name = 'event/event_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    The view for updating an event with all the necessary fields.
    """
    model = Post
    fields = [
        'title',
        'location',
        'content',
        'price',
        'attendance_limit',
        'waiting_list_limit',
        'start_date',
        'end_date',
        'image',
        'is_private'
    ]
    template_name = 'event/event_update.html'
    context_object_name = 'events'

    def form_valid(self, form):
        """
        Function for checking that the user input for the update is valid.
        :param form: The form including all the user input for the updated event.
        :return: A boolean value, true if the input is valid, false otherwise.
        """
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        """
        Checks that the requesting user fulfills the requirements for updating the event. If so, all users attending
        the event are notified and receives an email if they have activated notifications.
        :return: True if all requirments for the update are fulfilled, false otherwise.
        """
        event = self.get_object()
        if self.request.user == event.author or self.request.user in event.co_authors:
            email_list = []
            for user in event.attendees.all():
                if user.profile.on_event_update_delete:
                    email_list.append(user.email)
                    notification = Notification.objects.create(
                        user=user,
                        event=event,
                        text='{} {} has edited the event {}.'.format(
                            str(self.request.user.first_name),
                            str(self.request.user.last_name),
                            str(event.title)),
                        type='event'
                    )
                    user.profile.notifications.add(notification)
            if email_list.__len__() > 0:
                subject = event.title + " was updated!"
                from_email = settings.EMAIL_HOST_USER
                to_email = [user.email]
                message = event.title + " was updated. Please visit the event site to see the new updates."
                send_mail(subject=subject,
                          from_email=from_email,
                          recipient_list=to_email,
                          message=message,
                          fail_silently=False)

            return True
        return False


class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Class for deleting an event.
    """
    model = Post
    template_name = 'event/event_confirm_delete.html'
    success_url = '/'

    def test_func(self):
        """
        Checks that all requirements for deleting an event are fulfilled (that the requesting user is the author of the
        event). If the event is deleted all attendees with activated notifications are notified and receives an email.
        :return: True if all requirements are fulfilled, false otherwise.
        """
        event = self.get_object()
        if self.request.user == event.author:
            email_list = []
            for user in event.attendees.all():
                email_list.append(user.email)
                if user.profile.on_event_update_delete:
                    notification = Notification.objects.create(
                        user=user,
                        event=event,
                        text='{} {} has deleted the event {}.'.format(
                            str(self.request.user.first_name),
                            str(self.request.user.last_name),
                            str(event.title)),
                        type='home'
                    )
                    user.profile.notifications.add(notification)
            if email_list.__len__() > 0:
                subject = event.title + " was deleted!"
                from_email = settings.EMAIL_HOST_USER
                to_email = [user.email]
                message = event.title + " was deleted " \
                                        "by" + str(event.author.first_name) + " " + str(event.author.last_name) + "."
                send_mail(subject=subject,
                          from_email=from_email,
                          recipient_list=to_email,
                          message=message,
                          fail_silently=False)

            return True
        return False


class HtmlRender:

    def created_events(request):
        """
        :return: Returns a list of all the events created by the requesting user.
        """

        Utility.clean_ended_events(request.user);
        context = {
            'events': Post.objects.filter(author=request.user)
        }
        return render(request, 'event/created_events.html', context)

    def home_page(request):
        """
        :return: Returns two lists, one containing the four events starting closest from now and one with the rest
        of the events, except the private ones, and sends them to the home template.
        """
        Utility.clean_ended_events(request.user);
        events = Post.objects.filter(is_private=False).order_by('start_date')
        slide_events = events[0:4]
        context = {
            'slide_events': slide_events,
            'events': events
        }

        return render(request, 'event/home.html', context)

    @login_required
    def my_events(request):
        """
        Filters all events that has been joined or created by the requesting user and sends them to the template
        for displaying them.
        :return: A list of all events created or joined by the requesting user.
        """
        Utility.clean_ended_events(request.user);
        user = request.user

        # redirect if user not logged in
        try:
            created_events = Post.objects.filter(author=user)
            joined_events = Post.objects.filter(attendees=user)
        except TypeError:
            return redirect('users/templates/users/login.html')

        context = {
            'page': 'myEvents',
            'coverHeading': 'My Events',
            'created_events': created_events,
            'joined_events': joined_events
        }

        return render(request, 'event/my_events.html', context)

    @login_required
    def invite_list(request, event_id):
        """
        :param event_id: The primary key of the event the invite list is being retrieved for.
        :return: A list of all invited users to the event with pk=event_id.
        """
        user = request.user
        contacts = user.profile.contacts.all()

        # event_id = int(request.POST.get('event-id', False))
        event = Post.objects.get(pk=event_id)

        context = {
            'contacts': contacts,
            'event': event
        }

        return render(request, 'event/contacts.html', context)

    @login_required
    def attendee_list(request, event_id):
        """
        :param event_id: The primary key of the event the attendee list is being retrieved for.
        :return: A list of all attendees to the event with pk=event_id.
        """
        event = Post.objects.get(pk=event_id)

        attendees = event.attendees.all()

        context = {
            'attending': attendees,
            'event': event
        }

        return render(request, 'event/edit_attendees.html', context)


class EventViews:

    @login_required
    def event_join(request):
        """
        Function for joining an event. Retrieved the data necessary for getting the requested event. Checks that the
        user actually can join the event (enough spots etc.) and adds the user to the event attendee list. Triggers
        notification to the author of the event if the event is private.
        :return: Redirects the user to the detailed event page.
        """
        # get event
        event_id = int(request.POST.get('event-id', False))
        user = request.user
        event = Post.objects.get(pk=event_id)

        # get updated attendance count
        attendance = event.attendees.all().count()
        waiting = event.waiting_list.all().count()

        # create response
        if event.attendance_limit == 0 and event.waiting_list_limit == 0:
            messages.error(request, f'This even is not open for attendees yet. ')
        elif attendance + 1 > event.attendance_limit:
            if waiting + 1 > event.waiting_list_limit:
                messages.error(request, f'The event is already full.')
            else:
                event.waiting_list.add(user)
                messages.success(request, f'Signed up for the waiting list. ')
        elif event.author == user:
            messages.error(request, f"Can't sign up for your own event. ")
        elif user in event.attendees.all():
            messages.error(request, f'You are already signed up for this event.')
        else:
            if user.email != "":
                subject = "Successfully joined " + event.title + "!"
                from_email = settings.EMAIL_HOST_USER
                to_email = [user.email]
                message = "You successfully joined " + event.title + "! We look forward to seeing you there!"
                send_mail(subject=subject,
                          from_email=from_email,
                          recipient_list=to_email,
                          message=message,
                          fail_silently=False)

            # add user to event
            event.attendees.add(user)
            messages.success(request, f'You are now signed up for the event! ')

            if event.is_private and event.author.profile.on_event_invite:
                notification = Notification.objects.create(
                    user=event.author,
                    event=event,
                    text='{} signed up for your event.'.format(
                        str(user.first_name)),
                    type="person_joined"
                )
                event.author.profile.notifications.add(notification)

        if user in event.invited.all():
            event.invited.remove(user)
            user.profile.event_invites.remove(event)

        return redirect('event-detail', pk=event_id)

    @login_required
    def buy_ticket(request):
        """
        Logic for letting the user select which of its registered card to pay the ticket with.
        :return: A list of all credit card related to the requesting user, sent to the template for displaying.
        """
        event = Post.objects.get(pk=request.POST.get('event-id', False))
        cards = request.user.profile.credit_card.all()

        context = {
            'cards': cards,
            'event': event
        }

        return render(request, 'event/select_card.html', context)

    @login_required
    def redirect_to_execution(request):
        """
        Lets the user confirm that he wants to use the selected card for the purchase.
        :return: The selected card and the event the ticket is being purchased for and sends it to the template for
        confirmation of the transaction.
        """
        event_id = request.POST.get('event-id', False)
        credit_id = request.POST.get('card-id', False)
        event = Post.objects.get(pk=event_id)
        card = Credit.objects.get(pk=credit_id)

        context = {
            'card': card,
            'event': event
        }

        return render(request, 'event/confirm_transaction.html', context)

    @login_required
    def execute_transaction(request):
        """
        The actual execution of the purchase. Extracts all necessary information, buys the ticket, signs the user up
        for the event, withdraws the amount from the balance of the card. If the buying user has enabled notifications
        an email will be sent with a confirmation of the purchase.
        :return: Redirects the user to the detailed event page.
        """
        event_id = request.POST.get('event-id', False)
        event = Post.objects.get(pk=event_id)
        price = event.price
        user = request.user
        credit_id = request.POST.get('card-id', False)
        max_amount = user.profile.credit_card.get(pk=credit_id).amount

        if price > max_amount:
            messages.error(request, f'Not enough money on your credit card. ')
        else:
            if user.email != "":
                subject = "Transaction for" + event.title + " complete!"
                from_email = settings.EMAIL_HOST_USER
                to_email = [user.email]
                message = "You successfully payed" + str(
                    price) + " for " + event.title + "! We look forward to seeing you there!"
                send_mail(subject=subject,
                          from_email=from_email,
                          recipient_list=to_email,
                          message=message,
                          fail_silently=False)

            user.profile.credit_card.filter(pk=credit_id).update(amount=F('amount') - price)
            event.attendees.add(user)
            messages.success(request, f'Transaction complete! ')

        return redirect('event-detail', event_id)

    @login_required
    def event_decline_from_invitation(request):
        """
        Declines a received invitation and removes the declining user from the events' list of invited users.
        :return: Redirects the user to the page with all event invites.
        """
        event_id = int(request.POST.get('event-id', False))
        event = Post.objects.get(pk=event_id)
        user = request.user

        event.invited.remove(user)
        user.profile.event_invites.remove(event)

        messages.info(request, f'Invitation declined. ')

        return redirect('event-invites')

    @login_required
    def remove_attendee(request):
        """
        Function for removing an attending user from one of your event. Checks that the requesting user is
        authorized to perform the removal (author or co-host) and removes the selected user from the event.
        If the removed user has enabled notifications, he will receive an email and a notification.
        :return: Redirects the requesting user to the page displaying all attendees.
        """
        event_id = int(request.POST.get('event-id', False))
        event = Post.objects.get(pk=event_id)

        user_id = int(request.POST.get('user-id', False))
        user = User.objects.get(pk=user_id)

        if user in event.attendees.all():
            event.attendees.remove(user)
            messages.success(request, f'User removed from event')
            if event.is_private and user.profile.on_event_invite:
                if user.email != "":
                    subject = "You have been removed from " + event.title + "."
                    from_email = settings.EMAIL_HOST_USER
                    to_email = [user.email]
                    message = "A host removed you from the event " + event.title + "."
                    send_mail(subject=subject,
                              from_email=from_email,
                              recipient_list=to_email,
                              message=message,
                              fail_silently=False)

                notification = Notification.objects.create(
                    user=user,
                    event=event,
                    text='{} {} har removed you from their event.'.format(
                        str(request.user.first_name),
                        str(request.user.last_name)),
                    type="home"
                )
                user.profile.notifications.add(notification)

        return redirect('attendee-list', pk=event_id)

    @login_required
    def leave_event(request):
        """
        Logic for leaving an event that the requesting user is attending. Checks that the user is actually attending the
        event and removes it. If the event is private and the author has enabled notifications he will he notified. If
        the event has a waiting list and there are users in the waiting list, the first of those users will be promoted
        to the attendee list.
        :return: Redirects the leaving user to the detailed event page.
        """
        event_id = int(request.POST.get('event-id', False))
        user = request.user
        event = Post.objects.get(pk=event_id)

        if user in event.attendees.all():
            event.attendees.remove(user)
            messages.success(request, f'You are now signed off the event. ')

            if event.is_private and event.author.profile.on_event_invite:
                notification = Notification.objects.create(
                    user=event.author,
                    event=event,
                    text='{} {} is no longer going to your event.'.format(
                        str(user.first_name),
                        str(user.last_name)),
                    type="event"
                )
                event.author.profile.notifications.add(notification)
                if user.email != "":
                    subject = "Successfully signed off " + event.title + "!"
                    from_email = settings.EMAIL_HOST_USER
                    to_email = [user.email]
                    message = "You successfully signed oss from " + event.title + "! Sad to see you go :("
                    send_mail(subject=subject,
                              from_email=from_email,
                              recipient_list=to_email,
                              message=message,
                              fail_silently=False)

        else:
            messages.error(request, f"You can't sign off an event you're not signed up for. ")

        waiting = event.waiting_list.all().count()

        if waiting > 0:
            event.attendees.add(event.waiting_list.first())
            event.waiting_list.remove(event.waiting_list.first())

        return redirect('event-detail', pk=event_id)

    @login_required
    def leave_waiting_list(request):
        """
        Functionality for leaving the waiting list for an event. Checks that the user indeed is in the waiting list and
        removes it. If the event is private and the author has enabled notifications, the author is notified by email.
        :return:
        """
        # get event
        event_id = int(request.POST.get('event-id', False))
        user = request.user
        event = Post.objects.get(pk=event_id)

        if user in event.waiting_list.all():
            event.waiting_list.remove(user)
            messages.success(request, f'You are now signed off the event. ')

            if event.is_private and event.author.profile.on_event_invite:
                notification = Notification.objects.create(
                    user=event.author,
                    event=event,
                    text='{} {} is no longer in the waiting list for your event.'.format(
                        str(user.first_name),
                        str(user.last_name)),
                    type="event"
                )
                event.author.profile.notifications.add(notification)

        else:
            messages.error(request, f"You can't sign off the waiting list for an event you're not signed up for. ")

        return redirect('event-detail', pk=event_id)

    @login_required
    def redirect_notification(request, notification_id):
        """
        Logic for redirectin the user to a relevant page when a notification is being clicked.
        :param notification_id: The primary key of the clicked notification.
        :return: The page relevant for the particular type of notification.
        """
        notification = Notification.objects.get(pk=notification_id)

        Notification.objects.filter(pk=notification_id).read = True
        Notification.save(notification)

        if notification.type == 'event':
            event_id = notification.event.id
            return redirect('event-detail', event_id)
        elif notification.type == 'home':
            return redirect('event-home')
        elif notification.type == 'person_joined':
            event_id = notification.event.id
            return redirect('attendee-list', event_id)
        elif notification.type == 'new_request':
            return redirect('contact-requests')

        else:
            return redirect('profile')

    def search_events(request):
        """
        Searching algorithm for searching after specified events. Finds the events that contains the user input in its
        title and/or location. If some events matches both, these are displayed, if there are just events with one
        matchingm these are displayed, if there are none matches, no events are displayed.
        :return: The list of all events fulfilling the search requirements.
        """

        event_search = str(request.POST.get('event-search', False))
        location_search = str(request.POST.get('location-search', False))

        if len(location_search) == 0 or len(event_search) == 0:
            if len(location_search) == 0:
                if len(event_search) != 0:
                    location_search = "asdfasfgdsgsafasdas"

            if len(event_search) == 0:
                if len(location_search) != 0:
                    event_search = "asdfasfgdsgsafasdas"

        # filter for matching events and serialize for json
        title_search_results = list(Post.objects.filter(
            title__icontains=event_search
        ))

        location_search_results = list(Post.objects.filter(
            location__icontains=location_search
        ))

        best_match = []

        local = False
        for event in Post.objects.all():
            if event in title_search_results and event in location_search_results:
                local = True
                best_match.append(event)

        if local:
            event_search_results = best_match
        else:
            event_search_results = title_search_results + location_search_results

        if len(event_search_results) == 0:
            context = {
                'status': 'success',
                'message': 'No matches for your search.'
            }
        else:
            # create response
            context = {
                'status': 'success',
                'events': event_search_results
            }

        return render(request, "event/search.html", context)

    @login_required
    def invite_user(request):
        """
        Logic for inviting an user to one of your private events. If the invited user has enabled its notifications, he
        will be notified.
        :return: Redirects the inviter to the list of all possible users that can be invited.
        """
        event_id = int(request.POST.get('event-id', False))
        event = Post.objects.get(pk=event_id)
        user_id = int(request.POST.get('user-id', False))
        user = User.objects.get(pk=user_id)

        user.profile.event_invites.add(event)
        event.invited.add(user)

        if user.profile.on_event_invite:
            notification = Notification.objects.create(
                user=user,
                event=event,
                text='{} {} has sent you an invitation to their event.'.format(
                    str(request.user.first_name),
                    str(request.user.last_name)),
                type="event"
            )

            user.profile.notifications.add(notification)

        return redirect('invite-list', event_id)

    @login_required
    def cancel_invite(request):
        """
        Logic for withdrawing an invite. Checks that the invite is sent and removes it.
        :return: Redirects the inviter to the list of all possible users that can be invited.
        """
        event_id = int(request.POST.get('event-id', False))
        event = Post.objects.get(pk=event_id)
        user_id = int(request.POST.get('user-id', False))
        user = User.objects.get(pk=user_id)

        if user in event.invited.all():
            event.invited.remove(user)
            user.profile.event_invites.remove(event)

        return redirect('invite-list', event_id)

    @login_required
    def add_host(request):
        """
        Promotes an attendee to co-host. This allows the user to edit the attendee list, but not to update the event.
        :return: Redirects the inviter to the list of all possible users that can be invited.
        """
        event_id = int(request.POST.get('event-id', False))
        event = Post.objects.get(pk=event_id)
        user_id = int(request.POST.get('user-id', False))
        user = User.objects.get(pk=user_id)

        event.co_authors.add(user)

        messages.success(request, f'User successfully added as host. ')

        if user.profile.on_event_host:
            notification = Notification.objects.create(
                user=user,
                event=event,
                text='{} {} has added you as a administrator for the event {}.'.format(
                    str(request.user.first_name),
                    str(request.user.last_name),
                    str(event.title)),
                type="event"
            )

            user.profile.notifications.add(notification)

        return redirect('attendee-list', event_id)

    @login_required
    def remove_host(request):
        """
        Removes an attendee as co-host.
        :return: Redirects the inviter to the list of all possible users that can be invited.
        """
        event_id = int(request.POST.get('event-id', False))
        event = Post.objects.get(pk=event_id)
        user_id = int(request.POST.get('user-id', False))
        user = User.objects.get(pk=user_id)
        print(event_id)
        if user in event.co_authors.all():
            event.co_authors.remove(user)
            messages.info(request, f'User removed as admin')

        if user.profile.on_event_host:
            notification = Notification.objects.create(
                user=user,
                event=event,
                text='{} {} has removed you as a administrator for the event {}.'.format(
                    str(request.user.first_name),
                    str(request.user.last_name),
                    str(event.title)),
                type="event"
            )

            user.profile.notifications.add(notification)

        return redirect('attendee-list', pk=event_id)


class Utility:

    def toUTC(date, time, local_tz):
        # convert to localized dt obj
        aware_local_dt = local_tz.localize(
            datetime.strptime(
                '{} {}'.format(date, time),
                '%Y-%m-%d %H:%M'
            )
        )

        # convert to utc dt obj
        utc_dt = aware_local_dt.astimezone(pytz.utc)

        return utc_dt

    def clean_ended_events(self):
        """
        Deletes all events that took place back in time. This method is ran every time an user updates the website.
        :return: Nothing.
        """
        ended_events = Post.objects.filter(end_date__lte=datetime.utcnow())

        for event in ended_events:
            event.delete()

        return
