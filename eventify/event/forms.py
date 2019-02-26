from django import forms
from django.contrib.auth.models import User


class EventForm():   #Bruker crispyforms for å lettere opprette register form. Trenger da disse klassene
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['title', 'start_date', 'end_date', 'location', 'description']
        # fields sier hvilke felter vi skal ha med i registreringen. Hver attributt laster fra UserCreationForm, de er derfor ikke
        # navnsatt tilfeldig

