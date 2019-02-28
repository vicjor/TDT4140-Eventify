from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from users.models import Profile

# Create your models here.

class Post(models.Model):
    title = models.CharField(max_length=100)
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    attendees = models.ManyToManyField(User, related_name='attendees')
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    attendance_limit = models.IntegerField(null=True, default=10000)
    location = models.CharField(max_length=100, null=True)
    content = models.TextField()
    image = models.ImageField(default="default_event.jpg", upload_to="event_images")
    is_private = models.BooleanField(default=False)


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('event-detail', kwargs={'pk': self.pk}) #Etter man har opprettet et arrangement redigerer denne deg til eventet

    class Meta:
       ordering = ['-start_date']
