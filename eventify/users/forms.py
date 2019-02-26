from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class UserRegisterForm(UserCreationForm):   #Bruker crispyforms for å lettere opprette register form. Trenger da disse klassene
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']
        # fields sier hvilke felter vi skal ha med i registreringen. Hver attributt laster fra UserCreationForm, de er derfor ikke
        # navnsatt tilfeldig


class UserUpdateForm(forms.ModelForm):  # Brukes når en bruker ønsker å endre profilen sin. Har mulighet til å endre brukernavn og epost
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        # Bruker kan oppdatere fullt navn, brukernavn og epost

class ProfileUpdateForm(forms.ModelForm):   # Tillater bruker å laste opp eget profilbilde
    class Meta:
        model = Profile
        fields = ['image']