from django.test import TestCase
from .models import User, Profile
from django.test import Client
from unittest.mock import patch

# Create your tests here.

class UserTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        print("Setting up: UserTestCase")
        self.user1 = User.objects.create_user(username='Ole', email='ole@mail.no', password='ole')
        self.user2 = User.objects.create_user(username='Sjur', email='sjur@mail.no', password='sjur')
        self.profile1 = Profile.objects.create_profile(self.user1)
        self.profile2 = Profile.objects.create_profile(self.user2)

    def test_profile(self):
        self.assertTrue(len(Profile.objects.filter(username='Sjur')) == 1)
        self.assertTrue(len(Profile.objects.filter(username='Ole')) == 1)
        # Bruker kan velge å avregistrere seg senere #

    """def test_authenticated_user(self):
        self.c = Client()
        self.c.login(username='Ole', password='ole')
        self.c.login()"""