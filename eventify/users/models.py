from django.db import models
from django.contrib.auth.models import User
from event.models import Post
from PIL import Image #Brukes for bildehåndtering / profilbilde

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) #Er en 1-1 relasjon mellom bruker og profil
    image = models.ImageField(default="default.jpg", upload_to="profile_pics") #Profilbilde til bruker
    contacts = models.ManyToManyField(User, related_name="contacts")
    requests = models.ManyToManyField(User, related_name="requests")
    event_invites = models.ManyToManyField(Post, related_name="event_invites")
    sent_requests = models.ManyToManyField(User, related_name="sent_requests")


    def __str__(self):
        return self.user.id

    def save(self, *args, **kwargs):    #Brukes for å lagre etter å ha oppdatert bruker, *args og **kwargs gjør at vi kan sende inn flere argumenter i funksjonen
        super().save(*args, **kwargs)   #Bruker superklasse
        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300: #Skalerer ned alle bilder til max 300 x 300. Dette for å unngå unødvendig store filer, og at bilde bare brukes osm thumbnail.
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)


class Notification(models.Model):
    user = models.ForeignKey(Profile, on_delete = models.CASCADE) #Hvem som mottar varselet
    text = models.CharField(max_length=300) #Text i varselet
    time = models.DateTimeField() #Når man fikk varselet
    read = models.BooleanField(default=False) #har de sett varselet enda?
    link = models.URLField() #Link til side varselet omhandler
    sender = models.CharField(max_length=100) #Hvem/Hva utløste varselet?

    def __str__(self):
        return self.text






