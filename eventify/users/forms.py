from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Credit

class UserRegisterForm(UserCreationForm):
    """
    Form used by crispy forms in the user registration process. This class defines which fields that are to be
    included in the registration. The name of the fields must match those in the models.py file.
    """
    email = forms.EmailField()

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'password1',
            'password2'
        ]


class UserUpdateForm(forms.ModelForm):
    """
    Defines which fields that can be altered when updating your profile. Must match the fields in the models.py file.
    """
    email = forms.EmailField()

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email'
        ]


class ProfileUpdateForm(forms.ModelForm):
    """
    Defines what field(s) that can be altered when updating a profile.
    """
    class Meta:
        model = Profile
        fields = ['image']


class CreditCardRegisterForm(forms.ModelForm):
    """
    Defines the fields that are to be included when submitting a new credit card. The field names must match those in
    the models.py file.
    """

    class Meta:
        model = Credit
        fields = [
            'card_number',
            'security_code',
            'expiration_month',
            'expiration_year',
            'amount'
        ]
