from django import forms
from .models import Post


class UploadFileForm(forms.ModelForm):
    """
    Defines which fields of the event objects that are to be altered when using this specific form.
    """
    class Meta:
        model = Post
        file = forms.FileField()
        fields = ['image']
