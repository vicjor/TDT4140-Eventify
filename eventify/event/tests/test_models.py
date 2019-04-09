from django.test import TestCase
from django.contrib.auth.models import User
from event.models import Post


class PostTestCase(TestCase):
    def setUp(self):
        print("Setting up: PostTestCase")
        self.user1 = User.objects.create_user(username='Ole', email='ole@mail.no', password='oletest123')
        self.user2 = User.objects.create_user(username='Sjur', email='sjur@mail.no', password='sjurtest123')
        self.event1 = Post.objects.create(title='Strikkekveld', author=self.user1, location='Trondheim',
                                          content='Syk strikkekveld i Trondheim')
        self.event2 = Post.objects.create(title='Sykveld', author=self.user2, location='Oslo',
                                          content='Sykveld i hovedstaden')

    def test_author(self):
        self.assertEqual(str(self.event1.author), 'Ole')
        self.assertEqual(str(self.event2.author), 'Sjur')

    def test_pre_save_hook(self):
        self.event1.title = 'Heklekveld'
        self.event1.save()
        self.assertTrue(Post.objects.filter(title="Heklekveld").exists())

    def test_event_to_string(self):
        self.assertEqual(str(self.event1), self.event1.title)

    def test_absolute_url(self):
        self.assertFalse(self.event1.get_absolute_url() == self.event2.get_absolute_url())

    # def test_search(self):
    # def test_remove_event(self):
    # def test_update_event(self):
