from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.contrib.sessions import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Post
from django.contrib import messages
from django.utils import timezone
import pytz
import json
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

events = [
]

#Alt mellom START og END er alternativ kode for å vise events på siden. Men dette kan vi trykke på eventsene og komme inn på
#event/<event.id>, f.eks. http://127.0.0.1:8000/event/1.
#Foreløpig problem er at vi kommer inn på sidene, men det vises ingen info. http://127.0.0.1:8000/event/<event.id> extender
#bare base, og viser ingen info om eventet.

#START


class EventListView(ListView):  #Denne gjør at events vises på home i rekkefølge fra nyeste til eldste
    model = Post
    template_name = 'event/home.html' #<app>/<model>_<viewtype>.html
    context_object_name = 'events'
    ordering = ['-date_posted']

class EventDetailView(DetailView):
    model = Post
    template_name = 'event/event_detail.html'
    context_object_name = 'events'


class EventCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'attendance_limit']
    template_name = 'event/event_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'attendance_limit']
    template_name = 'event/event_form.html'
    context_object_name = 'events'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        event = self.get_object()
        if self.request.user == event.author:
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
            return True
        return False


class HtmlRender:

    def home(request):
        context = {
            'events': Post.objects.all()
        }
        return render(request, 'event/event.html', context)

    def homePage(request):
        events = Post.objects.all()
        bigEvent = Post.objects.first()
        context = {
            'bigEvent': bigEvent,
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
        events = Post.objects.all()


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

        return render(request, 'event/allEvents.html', context)

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

        return render(request, 'event/myEvents.html', context)

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
    def createEvent(request):
        new_title = str(request.POST.get('event-title', False)).title()
        new_start_date = str(request.POST.get('start_date', False))
        new_start_time = str(request.POST.get('start_time', False))
        new_end_date = str(request.POST.get('end_date', False))
        new_end_time = str(request.POST.get('end_time', False))
        new_location = str(request.POST.get('event-location', False))
        new_attendance_limit = int(request.POST.get('attendance-limit', False))
        new_content = str(request.POST.get('event-description', False))
        creator = request.user
        local_tz = pytz.timezone('Europe/Oslo')
        new_start_date = Utility.toUTC(new_start_date, new_start_time, local_tz)
        new_end_date = Utility.toUTC(new_end_date, new_end_time, local_tz)


        if new_start_date < datetime.now(pytz.utc):
            response = {
                'status': 'fail',
                'error_msg': 'Start date needs to be after current time.'
            }
        elif new_start_date > new_end_date:
            response = {
                'status': 'fail',
                'error_msg': 'Start date need to be before end date.'
            }
        else:
            # Create event
            event = Post.objects.create(
                title=new_title,
                author=creator,
                start_date=new_start_date,
                end_date=new_end_date,
                location=new_location,
                attendance_limit=new_attendance_limit,
                content=new_content
            )

            response = {
                'status': 'success',
                'event_id': event.id
            }

        return JsonResponse(response)

    @login_required
    def updateEvent(request, event_id):
        new_title = str(request.POST['event-title']).title()
        new_location = str(request.POST['event-location'])
        new_content = str(request.POST['event-description'])
        new_start_date = str(request.POST['edit-event-start-date'])
        new_start_time = str(request.POST['edit-event-start-time'])
        new_end_date = str(request.POST['edit-event-end-date'])
        new_end_time = str(request.POST['edit-event-end-time'])
        new_attendance_limit = str(request.POST['attendance_limit'])
        time_zone = request.session['django_timezone']
        local_tz = pytz.timezone(time_zone)
        event = get_object_or_404(Post, pk=event_id)

        # Update Event
        event.title =  new_title
        event.location = new_location
        event.content = new_content

        # handle start/end dt's
        try:
            start_date = Utility.toUTC(new_start_date, new_start_time, local_tz)
            end_date = Utility.toUTC(new_end_date, new_end_time, local_tz)

            if start_date < datetime.now(pytz.utc):
                response = {
                    'status': 'fail',
                    'error_msg': 'Start date needs to be after current time.'
                }
            elif start_date > end_date:
                response = {
                    'status': 'fail',
                    'error_msg': 'Start date need to be before end date.'
                }

            event.start_date = start_date
            event.end_date = end_date
        # if date was unaltered it came in as humanized string; pass
        except ValueError:
            pass

        try:
            if event.attendees.all().count() > new_attendance_limit:
                response = {
                    'status': 'fail',
                    'error_msg': 'Already too many attendees.'
                }
            event.attendance_limit = new_attendance_limit
        except ValueError:
            pass



        # Save updated event
        event.save()

        # create response
        response = {
            'status': 'success',
        }

        return JsonResponse(response)

    @login_required
    def removeEvent(request):
        event_id = json.loads(request.body)['post-id']
        event = get_object_or_404(Post, pk=event_id)

        # delete event
        if event.author == request.user:
            event.delete()

            # create response
            response = {
                'status': 'success',
            }
        else:
            response = {
                'status': 'fail',
                'error_msg': 'Cannot delete an event that you do not host.'
            }

        return JsonResponse(response)

    @login_required
    def eventJoin(request):
        # get event
        event_id = int(request.POST.get('event-id', False))
        user = request.user
        event = Post.objects.get(pk=event_id)

        # get updated attendance count
        attendance = event.attendees.all().count()

        # create response
        if attendance + 1 <= event.attendance_limit:
            messages.error(request, f'The event is already full.')
            return render(request, )
        elif len(event.attendees.filter(attendees__id=user.id)) == 1:
            messages.error(request, f'You are already signed up for this event.')
        else:
            # add user to event
            event.attendees.add(user)
            messages.success(request, f'You are now signed up for the event! ')


        # send reponse JSON
        return redirect("event-page", event_id=event.id)

    @login_required
    def leaveEvent(request):
        # get event
        event_id = int(request.POST.get('event-id', False))
        user = request.user
        event = Post.objects.get(pk=event_id)

        if event.attendees.filter(pk=user.id).first() != None:
            event.attendees.remove(user)
            response = {
                'status': 'success',
                'attendance': event.attendees.all().count()
            }

        else:
            response = {
                'status': 'fail',
                'error_msg': "Can't leave an event you haven't joined.",
                'attendance': event.attendees.all().count()
            }
        # send reponse JSON
        return JsonResponse(response)

    def search_events(request):

        event_search = str(request.POST.get('event-search', False))
        location_search = str(request.POST.get('location-search', False))
        date_start = str(request.POST.get('event-start', False))


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

    def eventDetails(request):
        # get event
        event_id = json.loads(request.body)['event_id']
        event = get_object_or_404(Post, pk=event_id)

        # serialize json
        serialized_event = serializers.serialize('json', [event])

        # create response
        response = {
            'status': 'success',
            'event': serialized_event
        }

        # send reponse JSON
        return JsonResponse(response)

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
