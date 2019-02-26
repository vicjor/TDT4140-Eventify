from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm


def register(request):      # Funksjon for å registrere bruker
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid(): # Sjekker at form er gyldig, og lagrer og oppretter bruker om den er det
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in.')
            return redirect('login') # Dirigerer deg til login siden når du har opprettet en bruker
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required # Triviell, men krever at bruker er logget inn for å kunne redigere bruker
def editProfile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid(): # Både user og profile må være gyldig
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile') #Redirigerer deg tilbake til profilen

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/editProfile.html', context)

@login_required #Du må være logget inn for å få tilgang til profilsiden. Sendes til registrering hvis ikke
def profile(request):
    user = request.user

    context = {
        'user': user
    }

    return render(request, 'users/profile.html', context)

