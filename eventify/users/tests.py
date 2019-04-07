from django.test import TestCase
from .models import User, Profile
from PIL import Image
from django.test import Client
from unittest.mock import patch

# Create your tests here.


@classmethod
def setUpClass(cls):
    pass


class ModelTestCase(TestCase):
    def setUp(self):
        print("Setting up: UserTestCase")
        self.user1 = User.objects.create_user(username='Ole', email='ole@mail.no', password='ole')
        self.user2 = User.objects.create_user(username='Sjur', email='sjur@mail.no', password='sjur')
        self.user1.id = 116
        self.user2.id = 117
        self.profile1 = Profile.objects.create(user=self.user1)
        self.profile2 = Profile.objects.create(user=self.user2)

    def test_profile(self):
        self.assertTrue(User.objects.filter(username='Sjur').count() == 1)
        self.assertTrue(User.objects.filter(username='Ole').count() == 1)

    def test_profile_to_string(self):
        self.assertEqual(str(self.profile1), str(self.profile1.user.id))

