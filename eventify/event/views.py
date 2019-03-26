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
import os
from django.conf import settings

events = [
]

#Alt mellom START og END er alternativ kode for å vise events på siden. Men dette kan vi trykke på eventsene og komme inn på
#event/<event.id>, f.eks. http://127.0.0.1:8000/event/1.
#Foreløpig problem er at vi kommer inn på sidene, men det vises ingen info. http://127.0.0.1:8000/event/<event.id> extender
#bare base, og viser ingen info om eventet.

#START

def handle_upload(request):
    if request.method == 'POST':
        p_form = UploadFileForm(request.POST, request.FILES, instance=request.user.profile)
        if p_form.is_valid(): # Både user og profile må være gyldig
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile') #Redirigerer deg tilbake til profilen

    else:
        p_form = UploadFileForm(instance=request.user.profile)

    context = {
        'p_form': p_form
    }
    return render(request, 'users/profile.html', context)


class EventListView(ListView):  #Denne gjør at events vises på home i rekkefølge fra nyeste til eldste
    model = Post
    template_name = 'event/home.html' #<app>/<model>_<viewtype>.html
    context_object_name = 'events'
    ordering = ['-date_posted']
    def get_queryset(self):
        return Post.objects.filter(is_private=False).order_by('-date_posted')

class UserListView(ListView):  #Denne gjør at events vises på home i rekkefølge fra nyeste til eldste
    model = Post
    template_name = 'event/user_posts.html' #<app>/<model>_<viewtype>.html
    context_object_name = 'events'
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')
    paginate_by = 6


class EventListAll(ListView):
    model = Post
    template_name = 'event/all_events.html'
    context_object_name = 'events'
    ordering = ['-date_posted']
    def get_queryset(self):
        events = Post.objects.filter(is_private=False).order_by('-date_posted')
        for event in events:
            if event.attendance_limit == event.attendees.all().count():
                events.filter(pk=event.id).delete()
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
    fields = ['title', 'location', 'content', 'price', 'attendance_limit', 'waiting_list_limit', 'start_date', 'end_date', 'image', 'is_private']
    template_name = 'event/event_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'location', 'content', 'price', 'attendance_limit', 'waiting_list_limit', 'start_date', 'end_date', 'image', 'is_private']
    template_name = 'event/event_form.html'
    context_object_name = 'events'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        event = self.get_object()
        if self.request.user == event.author or self.request.user in event.co_authors:
            for user in event.attendees:
                notification = Notification.objects.create(
                    user=user,
                    event=event,
                    text='{} {} has edited the event {}.'.format(self.request.user.first_name,
                                                                 self.request.user.last_name, event.title)
                )
                user.profile.notifications.add(notification)
            return True
        return False


#END

class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'event/event_confirm_delete.html'
    success_url = '/'

    def test_func(self):
        event = self.get_object()
        if self.request.user == event.author:
            for user in event.attendees:
                notification = Notification.objects.create(
                    user=user,
                    event=event,
                    text='{} {} has deleted the event {}.'.format(self.request.user.first_name,
                                                                 self.request.user.last_name, event.title)
                )
                user.profile.notifications.add(notification)
            return True
        return False


class HtmlRender:

    def created_events(request):

        context = {
            'events': Post.objects.filter(author=request.user)
        }
        return render(request, 'event/created_events.html', context)

    def home(request):

        context = {
            #'events': Post.objects.all()
            'events': Post.objects.filter(is_private=False)
        }
        return render(request, 'event/event.html', context)

    def homePage(request):
        events = Post.objects.filter(is_private=False).order_by('start_date')
        slide_events = events[0:4]
        context = {
            'slide_events': slide_events,
            'events': events
        }

        return render(request, 'event/home.html', context)

    def about(request):
        return render(request, 'event/about.html')

    @staff_member_required
    def createEventPage(request):
        context = {
            'page': 'createEvent',
            'coverHeading': 'Create Event'
        }
        return render(request, 'event/createEvent.html', context)

    def allEvents(request):
        #events = Post.objects.all()
        events = Post.objects.filter(is_private=False)

        for event in events:
            if event.attendance_limit <= event.attendees.all().count():
                events.remove(event)

        # Filter out users own events
        try:
            events = events.exclude(author=request.user)
        except TypeError:
            pass

        context = {
            'page': 'allEvents',
            'coverHeading': 'All Events',
            'events': events
        }

        return render(request, 'event/all_events.html', context)

    @login_required
    def myEvents(request):
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
        event = Post.objects.get(pk=event_id)

        attendees = event.attendees.all()

        context = {
            'attending': attendees,
            'event': event
        }

        return render(request, 'event/edit_attendees.html', context)


    @login_required
    def editEvent(request, event_id):
        event = get_object_or_404(Post, pk=event_id)

        # See if user can edit event
        if request.user == event.author:
            context = {
                'page': 'editEvent',
                'coverHeading': 'Edit Event',
                'event': event
            }
            return render(request, 'event/editEvent.html', context)
        else:
            return redirect(request, 'event/event.html')


class EventViews:

    @login_required
    def eventJoin(request):
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
            # add user to event
            event.attendees.add(user)
            messages.success(request, f'You are now signed up for the event! ')


        if user in event.invited.all():
            event.invited.remove(user)
            user.profile.event_invites.remove(event)

        if event.is_private:
            notification = Notification.objects.create(
                user=event.author,
                event=event,
                text='{} signed up for your event.'.format(user.first_name),
                type="profile"
            )
            event.author.profile.notifications.add(notification)

        return redirect('event-detail', pk=event_id)


    @login_required
    def buy_ticket(request):
        event = Post.objects.get(pk=request.POST.get('event-id', False))
        cards = request.user.profile.credit_card.all()

        context = {
            'cards': cards,
            'event': event
        }

        return render(request, 'event/confirm_transaction.html', context)

    @login_required
    def redirect_to_execution(request, credit_id):
        event_id = request.POST.get('event-id', False)
        event = Post.objects.get(pk=event_id)
        card = Credit.objects.get(pk=credit_id)

        context = {
            'card': card,
            'object': event
        }

        return render(request, 'event/execute_transaction.html', context)

    @login_required
    def execute_transaction(request, credit_id):
        event_id = request.POST.get('event-id', False)
        event = Post.objects.get(pk=event_id)
        price = event.price
        user = request.user
        max_amount = user.profile.credit_card.get(pk=credit_id).amount

        if price > max_amount:
            messages.error(request, f'Not enough money on your credit card. ')
        else:
            user.profile.credit_card.filter(pk=credit_id).update(amount=F('amount') - price)
            event.attendees.add(user)
            messages.success(request, f'Transaction complete! ')

        return redirect('event-detail', event_id)



    @login_required
    def event_decline_from_invitation(request):
        event_id = int(request.POST.get('event-id', False))
        event = Post.objects.get(pk=event_id)
        user = request.user

        event.invited.remove(user)
        user.profile.event_invites.remove(event)

        messages.info(request, f'Invitation declined. ')

        return redirect('event-invites')

    @login_required
    def remove_attendee(request):
        event_id = int(request.POST.get('event-id', False))
        event = Post.objects.get(pk=event_id)

        user_id = int(request.POST.get('user-id', False))
        user = User.objects.get(pk=user_id)

        if user in event.attendees.all():
            event.attendees.remove(user)
            messages.success(request, f'User removed from event')
            if event.is_private:
                notification = Notification.objects.create(
                    user=user,
                    event=event,
                    text='{} {} har removed you from their event.'.format(request.user.first_name, request.user.last_name),
                    type="profile"
                )
                user.profile.notifications.add(notification)

        return redirect('event-detail', pk=event_id)


    @login_required
    def leaveEvent(request):
        # get event
        event_id = int(request.POST.get('event-id', False))
        user = request.user
        event = Post.objects.get(pk=event_id)

        if user in event.attendees.all():
            event.attendees.remove(user)
            messages.success(request, f'You are now signed off the event. ')

            if event.is_private:
                notification = Notification.objects.create(
                    user=event.author,
                    event=event,
                    text='{} {} is no longer going to your event.'.format(user.first_name, user.last_name),
                    type="profile"
                )
                event.author.profile.notifications.add(notification)

        else:
            messages.error(request, f"You can't sign off an event you're not signed up for. ")

        waiting = event.waiting_list.all().count()

        if waiting > 0:
            event.attendees.add(event.waiting_list.first())
            event.waiting_list.remove(event.waiting_list.first())

        return redirect('event-detail', pk=event_id)

    @login_required
    def redirect_notification(request):
        user = request.user
        notification = Notification.objects.get(pk=request.POST.get('notification-id', False))

        user.profile.notifications.remove(notification)

        if notification.type == 'event':
            event_id = request.POST.get('event-id', False)
            return redirect('event-detail', event_id)
        else:
            return redirect('profile')





    def search_events(request):

        event_search = str(request.POST.get('event-search', False))
        location_search = str(request.POST.get('location-search', False))
        date_start = str(request.POST.get('event-start', False))

        if len(location_search) != 0 and len(event_search) != 0:
            if len(location_search) == 0:
                location_search = "asdfasfgdsgsafasdas"

            if len(event_search) == 0:
                event_search = "asdfasfgdsgsafasdas"



        # filter for matching events and serialize for json
        title_search_results = list(Post.objects.filter(
            title__icontains=event_search
        ))

        location_search_results = list(Post.objects.filter(
            location__icontains=location_search
        ))

        # date_search_result = list(Post.objects.filter(
        #    name_icontains=date_start
        # ).values(
        #    'start_date'
        # ))

        best_match = []

        local = False
        for event in Post.objects.all():
            if event in title_search_results and event in location_search_results:
                local = True
                best_match.append(event)


        if local:
            event_search_results = best_match
        else:
            event_search_results = title_search_results + location_search_results  # + date_search_result


        # reformat start dates
        #for i in event_search_results:
        #    i['start_date'] = i['start_date'].date()

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

        # return JsonResponse(context)

        # send response JSON
        return render(request, "event/search.html", context)


    @login_required
    def invite_user(request):
        event_id = int(request.POST.get('event-id', False))
        event = Post.objects.get(pk=event_id)
        user_id = int(request.POST.get('user-id', False))
        user = User.objects.get(pk=user_id)

        user.profile.event_invites.add(event)
        event.invited.add(user)

        notification = Notification.objects.create(
            user=user,
            event=event,
            text='{} {} has sent you an invitation to their event.'.format(request.user.first_name, request.user.last_name),
            type="event"
        )

        user.profile.notifications.add(notification)

        return redirect('invite-list', event_id)

    @login_required
    def cancel_invite(request):
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
        event_id = int(request.POST.get('event-id', False))
        event = Post.objects.get(pk=event_id)
        user_id = int(request.POST.get('user-id', False))
        user = User.objects.get(pk=user_id)

        event.co_authors.add(user)

        messages.success(request, f'User successfully added as host. ')

        notification = Notification.objects.create(
            user=user,
            event=event,
            text='{} {} has added you as a administrator for the event {}.'.format(request.user.first_name, request.user.last_name, event.title),
            type="event"
        )

        user.profile.notifications.add(notification)

        return redirect('event-detail', pk=event_id)

    @login_required
    def remove_host(request):
        event_id = int(request.POST.get('event-id', False))
        event = Post.objects.get(pk=event_id)
        user_id = int(request.POST.get('user-id', False))
        user = User.objects.get(pk=user_id)

        if user in event.co_authors.all():
            event.co_authors.remove(user)
            messages.info(request, f'User removed as admin')

        notification = Notification.objects.create(
            user=user,
            event=event,
            text='{} {} has removed you as a administrator for the event {}.'.format(request.user.first_name,
                                                                                   request.user.last_name, event.title),
            type="event"
        )

        user.profile.notifications.add(notification)

        return redirect('event-detail', pk=event_id)


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

    def cleanEndedEvents(self):
        # get end events
        ended_events = Post.objects.filter(end_date__lte=datetime.utcnow())

        for event in ended_events:
            event.delete()

        return
