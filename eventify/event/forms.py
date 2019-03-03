from django import forms
from django.contrib.auth.models import User
from .models import Post


class UploadFileForm(forms.Form):
    class Meta:
        model = Post
        file = forms.FileField()



