from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
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
    image = models.ImageField(default="default.jpg", upload_to="event_images")


    def __str__(self):
        return self.title

    class Meta:
       ordering = ['-start_date']


