from django import forms
from django.contrib.auth.models import User


class UploadFileForm(forms.Form):
    class Meta:
        model = Post
        file = forms.FileField()



