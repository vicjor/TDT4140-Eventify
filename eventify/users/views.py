from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .models import Notification, Credit
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.db.models import Q
from event.models import Post
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, CreditCardRegisterForm
from .models import Profile
from django.core.mail import send_mail, send_mass_mail


def register(request):
    """
    The function for the registration of new users. Takes in a request containing user input, checks that the forms is
    valid, if so the form is saved as a new profile. Otherwise relevant error messages are displayed.
    :param request: An HTTP request from user containing input.
    :return: Redirects the user to the login page if the input is valid, otherwise stays on the registration page.
    """
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Your account has been created! You are now able to log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def editProfile(request):
    """
    Functionality for updating an already existing profile. Checks that all user input is valid and executes the update.
    If the input is invalid relevant error messages are displayed.
    :param request: An HTTP request from user containing input.
    :return: Redirects the user to the profile page if the input is valid, otherwise stays on the update page.
    """
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')

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
    """
    Functionality for registration of credit cards related to the requesting user. Uses a help method to verify that all
    input is valid, if so the card is registered, otherwise relevant error messages are displayed.
    :param request: An HTTP request from user containing input.
    :return: Redirects the user to the profile page if the input is valid, otherwise stays on the registration page.
    """
    if request.method == 'POST':
        form = CreditCardRegisterForm(request.POST,
                                      instance=request.user)
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
    """
    Boolean function checking that all the user input for registrating a card is valid.
    :param card: Checks that the card number is 16 digits long.
    :param sec: Checks that the security code is 3 digits long.
    :param month: Checks that the month is an integer between 0 and 13.
    :param year: Checks that the year is a valid year (not before this date).
    :param amount: The amount the user wants to deposit to its card. Must be an integer.
    :return: True if all input is valid, false otherwise.
    """
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



@login_required
def profile(request):
    """
    Function for redirection the user to its profile page.
    :param request: An HTTP request.
    :return: Redirects the user to its profile.
    """
    user = request.user
    friends = user.profile.contacts.all()

    context = {
        'user': user,
        'friends': friends
    }

    return render(request, 'users/profile.html', context)


@login_required
def get_users(request):
    """
    :param request: An HTTP request.
    :return: Returns a list containing all users in the database to the template for displaying them.
    """
    users = User.objects.filter(~Q(pk=request.user.id))

    context = {
        'users': users
    }

    return render(request, 'users/all_users.html', context)


@login_required
def add_contact(request):
    """
    Function for sending a contact request to another user. Extracts necessary information to identify the added user
    and if the user is not already your contact it is added. If the added user has notifications on it will receive a
    notification and an email.
    :param request: An HTTP request.
    :return: Redirects the requesting user back to the page displaying all users.
    """
    user_id = int(request.POST.get('user-id', False))
    user = User.objects.get(pk=user_id)

    user.profile.requests.add(request.user)
    request.user.profile.sent_requests.add(user)

    if user.profile.on_event_invite:
        notification = Notification.objects.create(
            user=user,
            text='{} {} sent you a contact request'.format(
                str(request.user.first_name),
                str(request.user.last_name)),
            type="new_request"
        )

        user.profile.notifications.add(notification)

        if user.email != "":
            subject = str(request.user) + " sent you a friend request!"
            from_email = settings.EMAIL_HOST_USER
            to_email = [user.email]
            message = str(
                request.user) + " sent you a friend request! Follow this link " \
                                "to accept invitation: http://eventifypu.com/requests/"
            send_mail(subject=subject,
                      from_email=from_email,
                      recipient_list=to_email,
                      message=message,
                      fail_silently=False)

    messages.info(request, f'Request sent. ')

    return HttpResponseRedirect(reverse('all-users'))


@login_required
def see_requests(request):
    """
    Functions for getting all the contact requests of an users.
    :param request: An HTTP request.
    :return: A list of all contact request to the template displaying them.
    """
    requests = request.user.profile.requests.all()

    context = {
        'requests': requests
    }

    return render(request, 'users/contact_requests.html', context)


@login_required
def accept_request(request):
    """
    Logic for accepting a contact request. Extracts information needed to identify the user that sent the request. Adds
    the user to the list of your contacts and adds you to its list of contacts. Triggers a notification and an email.
    :param request: An HTTP request.
    :return: Returns the requesting user to the list of all requests.
    """
    user_id = int(request.POST.get('user-id', False))
    user = User.objects.get(pk=user_id)

    user.profile.sent_requests.remove(request.user)
    user.profile.contacts.add(request.user)

    request.user.profile.requests.remove(user)
    request.user.profile.contacts.add(user)

    if user.profile.on_event_invite:
        notification = Notification.objects.create(
            user=user,
            text='{} {} accepted your contact request.'.format(
                str(request.user.first_name),
                str(request.user.last_name)),
            type="profile"
        )

        user.profile.notifications.add(notification)

        if user.email != "":
            subject = str(request.user) + " accepted your friend request!"
            from_email = settings.EMAIL_HOST_USER
            to_email = [user.email]
            message = str(request.user) + " accepted your friend request! "
            send_mail(subject=subject,
                      from_email=from_email,
                      recipient_list=to_email,
                      message=message,
                      fail_silently=False)

    messages.success(request, f'Request has been accepted. ')

    return HttpResponseRedirect(reverse('contact-requests'))


@login_required
def decline_request(request):
    """
    Logic for declining a contact request. Identifies the user that sent the request and deletes it from the list of
    requests and deletes this user from the others list of users that have received requests.
    :param request: An HTTP request.
    :return: Redirects the user back to the list of all requests.
    """
    user_id = int(request.POST.get('user-id', False))
    user = User.objects.get(pk=user_id)

    user.profile.sent_requests.remove(request.user)

    request.user.profile.requests.remove(user)
    messages.info(request, f'Request has been declined. ')

    notification = Notification.objects.create(
        user=user,
        text='{} {} declined your contact request.'.format(
            str(request.user.first_name),
            str(request.user.last_name)),
        type="sent_requests"
    )

    user.profile.notifications.add(notification)

    return HttpResponseRedirect('contact-requests')

@login_required
def cancel_request(request):
    """
    Logic for withdrawing a contact request that has already been sent. Checks that the request has been sent, and
    deletes it.
    :param request: An HTTP request.
    :return: Redirects the user to the list of all users.
    """
    user_id = int(request.POST.get('user-id', False))
    user = User.objects.get(pk=user_id)

    if user in request.user.profile.sent_requests.all():
        request.user.profile.sent_requests.remove(user)
        user.profile.requests.remove(request.user)

    return HttpResponseRedirect(reverse('all-users'))


@login_required
def get_friends(request):
    """
    :param request: An HTTP request.
    :return: Returns the list of all the contacts of an user to the template for displaying them.
    """
    context = {
        'friends': request.user.profile.contacts.all()
    }

    return render(request, 'users/contacts.html', context)

@login_required
def remove_contact(request):
    """
    Logic for removing a contact from the requesting users' contact list. Checks that the contact is in fact in the
    contact list and if so, removes it.
    :param request: An HTTP request.
    :return: Redirects the user to the list of all contacts.
    """
    user_id = int(request.POST.get('user-id', False))
    user = User.objects.get(pk=user_id)

    if user in request.user.profile.contacts.all():
        request.user.profile.contacts.remove(user)
        user.profile.contacts.remove(request.user)
        messages.info(request, f'User successfully removed as contact.')

    return HttpResponseRedirect(reverse('contacts'))

@login_required
def search_user(request):
    """
    Searching algorithm for searching after users. Checks if the user input is contained within the username, first
    name or last name and returns all the users that matches.
    :param request: An HTTP request.
    :return: A list of all users containing the user input in one of the mentioned fields and sends this list to the
    template for displaying.
    """
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
    """
    Searching algorithm for searching after users within an event. Checks if the user input is contained within the
    username, first name or last name and returns all the users that matches.
    :param request: An HTTP request.
    :return: A list of all users containing the user input in one of the mentioned fields and sends this list to the
    template for displaying.
    """
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
    """
    Retrieves all the invites to events for the requesting user.
    :param request: An HTTP request.
    :return: Returns a list of all event invites and sends this list to the template for displaying them.
    """

    event = request.user.profile.event_invites.all()

    context = {
        'invites': event
    }

    return render(request, 'users/event_invites.html', context)

@login_required
def get_credit_cards(request):
    """
    Retrieves all the credit cards for the requesting user.
    :param request: An HTTP request.
    :return: Returns a list of all credit cards and sends this list to the template for displaying them.
    """
    profile = request.user.profile

    context = {
        'cards': profile.credit_card.all()
    }

    return render(request, 'users/get_cards.html', context)

@login_required
def change_on_contact(request):
    profile = request.user.profile

    if profile.on_contact:
        profile.on_contact = False
        profile.save()
    else:
        profile.on_contact = True
        profile.save()

    messages.success(request, f'Settings successfully changed. ')

    return redirect('to-notifications')


@login_required
def change_event_invite(request):
    """
    Change the boolean variable for the notification setting for this type of notifications.
    :param request: An HTTP request.
    :return: Redirects the user to the template where the
    """
    profile = request.user.profile

    if profile.on_event_invite:
        profile.on_event_invite = False
        profile.save()
    else:
        profile.on_event_invite = True
        profile.save()

    messages.success(request, f'Settings successfully changed. ')

    return redirect('to-notifications')


@login_required
def change_on_event_update_delete(request):
    """
    Change the boolean variable for the notification setting for this type of notifications.
    :param request: An HTTP request.
    :return: Redirects the user to the template where the
    """
    profile = request.user.profile

    if profile.on_event_update_delete:
        profile.on_event_update_delete = False
        profile.save()
    else:
        profile.on_event_update_delete = True
        profile.save()

    messages.success(request, f'Settings successfully changed. ')

    return redirect('to-notifications')


@login_required
def change_on_event_host(request):
    """
    Change the boolean variable for the notification setting for this type of notifications.
    :param request: An HTTP request.
    :return: Redirects the user to the template where the
    """
    profile = request.user.profile

    if profile.on_event_host:
        profile.on_event_host = False
        profile.save()
    else:
        profile.on_event_host = True
        profile.save()

    messages.success(request, f'Settings successfully changed. ')

    return redirect('to-notifications')
@login_required
def redirect_to_not(request):
    """
    Handles the redirection of a user clicking a notification. Redirects the user to a relevant page.
    :param request: An HTTP request.
    :return: Redirects the user to a relevant page in terms of the notification clicked.
    """
    user = request.user

    context = {
        'user': user
    }

    return render(request, 'event/edit_notifications.html', context)

@login_required
def delete_notifications(request):
    """
    Function for deleting all notifications from this user.
    :param request: An HTTP request
    :return: Redirects the user to the home page after the notifcations has been deleted.
    """
    profile = request.user.profile

    for notification in profile.notifications.all():
        profile.notifications.remove(notification)

    profile.save()
    return redirect('event-home')
