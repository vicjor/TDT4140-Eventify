from django.test import TestCase, RequestFactory, Client
from .models import Post
from users.models import *
from .forms import UploadFileForm
from .urls import urlpatterns
from django.contrib.auth.models import User
from django.urls import resolve
from django.urls import reverse
from users.models import Profile


# Create your tests here.
class FormsTestCase(TestCase):
    def test_valid_form(self):
        form_data = {'something'}
        form = UploadFileForm(data=form_data)
        self.assertTrue(form.is_valid())


# Integration test of Event's functionality from the users "view"
class TestEvent(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='ole', email='ole@mail.no', password='oletest123')
        self.user2 = User.objects.create_user(username='sjur', email='sjur@mail.no', password='sjurtest123')
        self.event1 = Post.objects.create(title='Strikkekveld', author=self.user1, location='Trondheim',
                                          content='Syk strikkekveld i Trondheim', id=123)
        self.event2 = Post.objects.create(title='Sykveld', author=self.user2, location='Oslo',
                                          content='Sykveld i hovedstaden', id=124)
        self.c = Client(HTTP_USER_AGENT='Mozilla/5.0')

    def test_join_event_denies_anonymous(self):
        response = self.c.post('/event/join/', follow=True)
        self.assertRedirects(response, '/login/?next=/event/join/')

    def test_join_and_leave_event(self):
        self.c.login(username='ole', password='oletest123')
        response = self.c.post('/event/join/', {'event-id': self.event2.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        response = self.c.post('/event/leave/', {'event-id': self.event2.id}, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_invite_friend_and_cancel_invite(self):
        self.c.login(username='ole', password='oletest123')
        response = self.c.get('/invite-friends/123/', follow=True)
        self.assertEqual(response.status_code, 200)
        response = self.c.post('/send-invite/', {'event-id':self.event2.id, 'user-id':self.user2.id}, follow = True)
        self.assertEqual(response.status_code, 200)
        response = self.c.post('/cancel-invite/', {'event-id':self.event2.id, 'user-id':self.user2.id}, follow = True)
        self.assertEqual(response.status_code,200)

    def create_and_delete_event(self):
        #Denne er jeg veldig usikker på om faktisk tester noe fornuftig, men den er nå her.
        self.c.login(username='ole', password='oletest123')
        response = self.c.post('/event/new/',{'id':3}, follow=True)
        self.assertEqual(response.status_code,200)
        response=self.c.get('/event/3')
        self.assertEqual(response.status_code,200)
        response=self.c.post('/event/3/delete/', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_home_page(self):
        response = self.c.get('/')
        self.assertEqual(response.status_code, 200)



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

