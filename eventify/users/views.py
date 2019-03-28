from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .models import Notification, Credit
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from event.models import Post
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, CreditCardRegisterForm
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

@login_required
def register_credit(request):
    if request.method == 'POST':
        form = CreditCardRegisterForm(request.POST, instance=request.user)
        data = request.POST.copy()
        card_n = data.get('card_number')
        sec_code = data.get('security_code')
        exp_m = data.get('expiration_month')
        exp_y = data.get('expiration_year')
        amount = data.get('amount')
        if check_valid_card(card_n, sec_code, exp_m, exp_y, amount):
            card = Credit.objects.create(
                card_number=card_n,
                security_code=sec_code,
                expiration_month=exp_m,
                expiration_year=exp_y,
                amount=amount
            )
            card.save()
            request.user.profile.credit_card.add(card)
            form.save()
            messages.success(request, f'Credit card has been registered')
            return redirect('profile')
        else:
            messages.error(request, f'Check over your input, something went wrong. ')
    else:
        messages.error(request, f'Check over your input, something went wrong. ')
        form = CreditCardRegisterForm(instance=request.user)

    context = {
        'form': form
    }
    return render(request, 'users/register_card.html', context)

def check_valid_card(card, sec, month, year, amount):
    if len(card) != 16 or not card.isdigit():
        return False
    if len(sec) != 3 or not sec.isdigit():
        return False
    if len(month) != 2 or not month.isdigit() or int(month) > 12 or int(month) < 1:
        return False
    if len(year) != 2 or not year.isdigit() or int(year) < 19:
        return False
    if int(amount) < 0:
        return False
    return True



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

    notification = Notification.objects.create(
        user=user,
        text='{} {} sent you a contact request'.format(str(request.user.first_name), str(request.user.last_name)),
        type="new_request"
    )

    user.profile.notifications.add(notification)

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

    notification = Notification.objects.create(
        user=user,
        text='{} {} accepted your contact request.'.format(str(request.user.first_name), str(request.user.last_name)),
        type="profile"
    )

    user.profile.notifications.add(notification)

    messages.success(request, f'Request has been accepted. ')

    return HttpResponseRedirect(reverse('contact-requests'))


@login_required
def decline_request(request):
    user_id = int(request.POST.get('user-id', False))
    user = User.objects.get(pk=user_id)

    user.profile.sent_requests.remove(request.user)

    request.user.profile.requests.remove(user)
    messages.info(request, f'Request has been declined. ')

    notification = Notification.objects.create(
        user=user,
        text='{} {} declined your contact request.'.format(str(request.user.first_name), str(request.user.last_name)),
        type="sent_requests"
    )

    user.profile.notifications.add(notification)

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

@login_required
def new_notifications_count(request):
    profile = request.user.profile
    counter = 0;

    for notification in profile.notifications:
        if not notification.read:
            counter += 1

    return counter;

@login_required
def get_credit_cards(request):
    profile = request.user.profile

    context = {
        'cards': profile.credit_card.all()
    }

    return render(request, 'users/get_cards.html', context)

