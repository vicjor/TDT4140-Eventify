from django.test import TestCase
from eventify.event.models import Post
from django.contrib.auth.models import User
from unittest.mock import patch
# Create your tests here.


class PostTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        print("Setting up: PostTestCase")
        self.user1 = User.objects.create_user(username='Ole', email='ole@mail.no', password='ole')
        self.user2 = User.objects.create_user(username='Sjur', email='sjur@mail.no', password='sjur')
        self.event1 = Post.objects.create(title='Strikkekveld', author=self.user1, location='Trondheim',
                                          content='Syk strikkekveld i Trondheim')
        self.event2 = Post.objects.create(title='Sykveld', author=self.user2, location='Oslo',
                                          content='Sykveld i hovedstaden')
        self.user1.eventJoin(self.event2)
        self.user2.eventJoin(self.event1)

    def test_author(self):
        self.assertEqual(self.event1.author, 'Ole')
        self.assertEqual(self.event2.author, 'Sjur')

    def test_join_event(self):
        self.assertTrue(self.user1 in self.event2.attendees().all())
        self.assertTrue(self.user2 in self.event1.attendees().all())

    def test_leave_event(self):
        self.user1.eventLeave(self.event2)
        self.user2.eventLeave(self.event1)
        self.assertTrue(self.user1 not in self.event2.attendees().all())
        self.assertTrue(self.user2 not in self.event1.attendees().all())

    def test_pre_save_hook(self):
        self.event1.title = 'Heklekveld'
        self.event1.save()
        self.assertTrue(Post.objects.filter(title="Heklekveld").exists())

    def test_event_to_string(self):
        self.assertEqual(self.event1.__str__(), "Strikkekveld")

    # def test_search(self):
    # def test_remove_event(self):
    # def test_update_event(self):
