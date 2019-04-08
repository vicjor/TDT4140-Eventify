from django.db import models
from django.contrib.auth.models import User
from event.models import Post
from django.utils import timezone
from django.core.validators import RegexValidator
from PIL import Image #Brukes for bildehåndtering / profilbilde


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Hvem som mottar varselet
    event = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    text = models.CharField(max_length=300) # Text i varselet
    time = models.DateTimeField(default=timezone.now) # Når man fikk varselet
    read = models.BooleanField(default=False) # har de sett varselet enda?
    link = models.URLField() # Link til side varselet omhandler
    sender = models.CharField(max_length=100) # Hvem/Hva utløste varselet?
    type = models.CharField(max_length=10, default="profile")

    class Meta:
        ordering = ['-time']

    def __str__(self):
        return self.text

class Credit(models.Model):
    card_number = models.CharField(max_length=16, validators=[RegexValidator(r'^[0-9]{16}$')])
    security_code = models.CharField(max_length=3, validators=[RegexValidator(r'^[0-9]{3}$')])
    expiration_month = models.CharField(max_length=2, validators=[RegexValidator(r'^[0-9]{2}$')])
    expiration_year = models.CharField(max_length=2, validators=[RegexValidator(r'^[0-9]{2}$')])
    amount = models.IntegerField()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) #Er en 1-1 relasjon mellom bruker og profil
    credit_card = models.ManyToManyField(Credit, related_name="credit_card")
    image = models.ImageField(default="default.jpg", upload_to="profile_pics") #Profilbilde til bruker
    contacts = models.ManyToManyField(User, related_name="contacts")
    requests = models.ManyToManyField(User, related_name="requests")
    event_invites = models.ManyToManyField(Post, related_name="event_invites")
    sent_requests = models.ManyToManyField(User, related_name="sent_requests")
    notifications = models.ManyToManyField(Notification, related_name="notifications")
    on_contact = models.BooleanField(default=True, null=True)
    on_event_invite = models.BooleanField(default=True)
    on_event_update_delete = models.BooleanField(default=True)
    on_event_host = models.BooleanField(default=True)

    def __str__(self):
        """
        "To string"-method. Defines what that is to be returned when someone prints out an instance of this model.
        :return: The ID of the user it is called upon.
        """
        return str(self.user.id)

    def save(self, *args, **kwargs):
        """
        Function for saving an updated user
        :param args: Making sure that the function accepts more than one argument.
        :param kwargs: Making sure that the function accepts more than one argument.
        :return: Saves the image.
        """
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)











