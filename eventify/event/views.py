from django.shortcuts import render
from .models import Post

events = [
]

# Create your views here.
def home(request):
    context = {
        'events': Post.objects.all()
    }
    return render(request, 'event/event.html', context)

def about(request):
    return render(request, 'event/about.html')




