from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    When a user is created, this function is alerted and creates a corresponding profile.
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return: Creates a profile to the requesting user.
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
