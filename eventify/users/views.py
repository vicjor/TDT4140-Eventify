from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from event.models import Post
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile


def register(request):  # Funksjon for å registrere bruker
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():  # Sjekker at form er gyldig, og lagrer og oppretter bruker om den er det
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in.')
            return redirect('login')  # Dirigerer deg til login siden når du har opprettet en bruker
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required  # Triviell, men krever at bruker er logget inn for å kunne redigere bruker
def editProfile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():  # Både user og profile må være gyldig
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')  # Redirigerer deg tilbake til profilen

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/editProfile.html', context)


@login_required  # Du må være logget inn for å få tilgang til profilsiden. Sendes til registrering hvis ikke
def profile(request):
    user = request.user
    friends = user.profile.contacts.all();

    context = {
        'user': user,
        'friends': friends
    }

    return render(request, 'users/profile.html', context)


@login_required
def get_users(request):
    users = User.objects.filter(~Q(pk=request.user.id))

    context = {
        'users': users
    }

    return render(request, 'users/all_users.html', context)


@login_required
def add_contact(request):
    user_id = int(request.POST.get('user-id', False))
    user = User.objects.get(pk=user_id)

    user.profile.requests.add(request.user)
    request.user.profile.sent_requests.add(user)

    messages.info(request, f'Request sent. ')

    return HttpResponseRedirect(reverse('all-users'))


@login_required
def see_requests(request):
    requests = request.user.profile.requests.all()

    context = {
        'requests': requests
    }

    return render(request, 'users/contact_requests.html', context)


@login_required
def accept_request(request):
    user_id = int(request.POST.get('user-id', False))
    user = User.objects.get(pk=user_id)

    user.profile.sent_requests.remove(request.user)
    user.profile.contacts.add(request.user)

    request.user.profile.requests.remove(user)
    request.user.profile.contacts.add(user)

    messages.success(request, f'Request has been accepted. ')

    return HttpResponseRedirect(reverse('contact-requests'))


@login_required
def decline_request(request):
    user_id = int(request.POST.get('user-id', False))
    user = User.objects.get(pk=user_id)

    user.profile.sent_requests.remove(request.user)

    request.user.profile.requests.remove(user)
    messages.info(request, f'Request has been declined. ')

    return HttpResponseRedirect('contact-requests')

@login_required
def cancel_request(request):
    user_id = int(request.POST.get('user-id', False))
    user = User.objects.get(pk=user_id)

    if user in request.user.profile.sent_requests.all():
        request.user.profile.sent_requests.remove(user)
        user.profile.requests.remove(request.user)

    return HttpResponseRedirect(reverse('all-users'))


@login_required
def get_friends(request):

    context = {
        'friends': request.user.profile.contacts.all()
    }

    return render(request, 'users/contacts.html', context)

@login_required
def remove_contact(request):
    user_id = int(request.POST.get('user-id', False))
    user = User.objects.get(pk=user_id)

    if user in request.user.profile.contacts.all():
        request.user.profile.contacts.remove(user)
        user.profile.contacts.remove(request.user)
        messages.info(request, f'User successfully removed as contact.')

    return HttpResponseRedirect(reverse('profile'))

@login_required
def search_user(request):
    search = str(request.POST.get('search-field', False))

    search_result = list(User.objects.filter(
        Q(username__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search)
    ))

    context = {
        'users': search_result
    }

    return render(request, 'users/all_users.html', context)

@login_required
def search_user_event(request):
    search = str(request.POST.get('search-field', False))
    event = Post.objects.get(pk=int(request.POST.get('event-id', False)))


    search_result = list(event.attendees.filter(
        Q(username__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search)
    ))

    context = {
        'attending': search_result,
        'event': event
    }

    return render(request, 'event/edit_attendees.html', context)

@login_required
def event_invites(request):

    event = request.user.profile.event_invites.all()

    context = {
        'invites': event
    }

    return render(request, 'users/event_invites.html', context)

