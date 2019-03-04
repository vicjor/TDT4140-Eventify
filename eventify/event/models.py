from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image


# Create your models here.

class Post(models.Model):
    title = models.CharField(max_length=100)
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    attendees = models.ManyToManyField(User, related_name='attendees')
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    attendance_limit = models.IntegerField(null=True, default=10000, blank=True)
    location = models.CharField(max_length=100, null=True)
    content = models.TextField()
    image = models.ImageField(default="default_event.jpg", upload_to="event_images", blank=True)
    is_private = models.BooleanField(default=False)


    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):    #Brukes for å lagre etter å ha oppdatert bruker, *args og **kwargs gjør at vi kan sende inn flere argumenter i funksjonen
        super().save(*args, **kwargs)   #Bruker superklasse
        img = Image.open(self.image.path)


    def get_absolute_url(self):
        return reverse('event-detail', kwargs={'pk': self.pk}) #Etter man har opprettet et arrangement redigerer denne deg til eventet

    class Meta:
       ordering = ['-start_date']
