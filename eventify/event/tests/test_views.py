from django.test import SimpleTestCase, RequestFactory, Client
from django.contrib.auth.models import User

from users.models import *
from event.models import Post


# Integration test of Event's functionality from the users "view"
class TestEvent(SimpleTestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='OleSuperDuper', email='ole@mail.no')
        self.user1.set_password('oletest123')
        self.user1.id = 116

        self.profile1 = Profile.objects.create(user=self.user1)

        self.user2 = User.objects.create_user(username='SjurSuperDuper', email='sjur@mail.no')
        self.user2.set_password('sjurtest123')
        self.user2.id = 117

        self.profile2 = Profile.objects.create(user=self.user2)

        self.event1 = Post.objects.create(title='Strikkekveld', author=self.user1, location='Trondheim',
                                          content='Syk strikkekveld i Trondheim')
        self.event1.save()
        self.event2 = Post.objects.create(title='Sykveld', author=self.user2, location='Oslo',
                                          content='Sykveld i hovedstaden')
        self.event2.save()

        self.c = Client(HTTP_USER_AGENT='Mozilla/5.0')

    def test_join_event_denies_anonymous(self):
        response = self.c.get('/event/join/', follow=True)
        self.assertRedirects(response, '/login/?next=/event/join/')

    def test_join_and_leave_event(self):
        self.c.post('/login/', {'username': self.user1.username, 'password': self.user1.password})
        response = self.c.get('/event/join/', follow=True, title='Sykveld')
        self.assertEqual(response.status_code, 200)

    """def test_call_view_fails_blank(self):
        self.client.login(username='user', password='test')
        response = self.client.post('/url/to/view', {}) # blank data dictionary
        self.assertFormError(response, 'form', 'some_field', 'This field is required.')
        # etc. ...


    def test_call_view_fails_invalid(self):
        # as above, but with invalid rather than blank data in dictionary

    def test_call_view_fails_invalid(self):
        # same again, but with valid data, then
        self.assertRedirects(response, '/contact/1/calls/')
    """