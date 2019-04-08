from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image
from django.views.generic import ListView


# Create your models here.

class Post(models.Model):
    title = models.CharField(max_length=100)
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    co_authors = models.ManyToManyField(User, related_name='co_authors')
    price = models.FloatField(default=0, blank=True, null=True)
    attendees = models.ManyToManyField(User, related_name='attendees')
    waiting_list = models.ManyToManyField(User, related_name='waiting_list')
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    attendance_limit = models.PositiveIntegerField(null=True, default=10000, blank=True)
    waiting_list_limit = models.PositiveIntegerField(null=True, default=0, blank=True, )
    location = models.CharField(max_length=100, null=True)
    content = models.TextField()
    image = models.ImageField(default="default_event.jpg", upload_to="event_images", blank=True)
    is_private = models.BooleanField(default=False)
    invited = models.ManyToManyField(User, related_name="invited")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Method for saving the event after it has been updated.
        :param args: Makes the function capable of taking more than one argument.
        :param kwargs: Makes the function capable of taking more than one argument.
        :return: Returns the user back to the event that has just been updated.
        """
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)

    def get_absolute_url(self):
        """
        :return: Returns the absolute URL of the detailed event page.
        """
        return reverse('event-detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['start_date']


class PostListView(ListView):
    model = Post
    template_name = 'event/search.html'
    paginate_by = 6
