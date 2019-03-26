from django.contrib import admin
from .models import Profile, Credit, Notification

admin.site.register(Profile) #Legger til profil på adminpanel
admin.site.register(Credit)
admin.site.register(Notification)

