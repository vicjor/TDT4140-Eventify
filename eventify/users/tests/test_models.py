from django.test import TestCase
from django.contrib.auth.models import User
from users.models import Profile

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

"""
    def test_profile_pre_save_hook(self):
        file_mock = mock.MagicMock(name='FileMock', spec=ContentFile)
        self.profile1.image = file_mock
        self.profile1.save()
        self.assertTrue(Profile.objects.filter(image="test_image.jpg").exists())
        self.assertEqual(self.profile1.image.size, (300, 300))
"""