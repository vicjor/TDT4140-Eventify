from django.test import TestCase
from .models import Post
from django.contrib.auth.models import User
# Create your tests here.

class PostTestCase(TestCase):
    def setUp(self):
        user1 = User.objects.create_user(username='Ole', email='ole@mail.no', password='ole')
        user2 = User.objects.create_user(username='Ole', email='ole@mail.no', password='ole')
        user3 = User.objects.create_user(username='Ole', email='ole@mail.no', password='ole')
        user4 = User.objects.create_user(username='Ole', email='ole@mail.no', password='ole')
        Post.objects.create(title='Strikkekveld', author=user1, location='Trondheim',
                            content='Syk strikkekveld i Trondheim')
        Post.objects.create(title='Sykveld', author=user2, location='Oslo',
                            content='Sykveld i hovedstaden')
        Post.objects

