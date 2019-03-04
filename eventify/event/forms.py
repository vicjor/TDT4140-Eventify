from django import forms
from .models import Post


class UploadFileForm(forms.ModelForm):
    class Meta:
        model = Post
        file = forms.FileField()
        fields = ['image']





