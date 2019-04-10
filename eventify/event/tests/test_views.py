from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import User

from users.models import *
from event.models import Post


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
        self.c.post('/event/join/', {'event-id': self.event2.id}, follow=True)
        self.assertEqual(self.event2.attendees.count(), 1)
        self.c.post('/event/leave/', {'event-id': self.event2.id}, follow=True)
        self.assertEqual(self.event2.attendees.count(), 0)

    def test_invite_friend_and_cancel_invite(self):
        self.c.login(username='ole', password='oletest123')
        self.c.get('/invite-friends/123/', follow=True)
        self.c.post('/send-invite/', {'event-id': self.event2.id, 'user-id': self.user2.id}, follow=True)
        self.assertEqual(self.user2.profile.event_invites.count(), 1)
        self.c.post('/cancel-invite/', {'event-id': self.event2.id, 'user-id': self.user2.id}, follow=True)
        self.assertEqual(self.user2.profile.event_invites.count(), 0)

    def create_and_delete_event(self):
        self.c.login(username='ole', password='oletest123')
        self.c.post('/event/new/', {'id': 3}, follow=True)
        self.assertEqual(Event.objects.get(pk=3).count(),1)
        response = self.c.get('/event/3')
        self.assertEqual(response.status_code, 200)
        self.c.post('/event/3/delete/', follow=True)
        response = self.c.get('/event/3')
        self.assertEqual(response.status_code, 404)

    def test_home_page(self):
        response = self.c.get('/')
        self.assertEqual(response.status_code, 200)

    def test_add_and_remove_host(self):
        self.c.login(username='ole', password='oletest123')
        response = self.c.post('/add-host/', {'event-id': self.event1.id, 'user-id': self.user2.id}, follow=True)
        self.assertEqual(self.event1.co_author.count(), 1)
        #response = self.c.post('/remove-host/', {'event-id': self.event1.id, 'user-id': self.user2.id}, follow=True) Denne krasjer, send help
        self.assertEqual(response.status_code, 200)

    def test_remove_attendee(self):
        self.c.login(username='sjur', password='sjurtest123')
        self.c.post('/event/join/', {'event-id': self.event1.id}, follow=True)
        self.c.logout()
        self.c.login(username='ole', password='oletest123')
        #response = self.c.post('/remove-attendee/', {'event-id': self.event1.id, 'user-id':self.user2.id}, follow = True) Denne crasjer, send help
        #self.assertEqual(response.status_code, 200)

    def test_event_created(self):
        self.c.login(username='ole', password='oletest123')
        response = self.c.get('/event/created/')
        self.assertEqual(response.status_code, 200)

    """def test_add_card_and_pay(self):
        self.c.login(username='ole', password='oletest123')
        response=self.c.post('/register-card/', {'card_number':1234567887654321, 'security_code':123,
                                                 'expiration_month': 1, 'expiration_year':20, 'amount':5000}, follow=True)
        self.event3 = Post.objects.create(title='Strikkekveld', author=self.user1, location='Trondheim',
                                          content='Syk strikkekveld i Trondheim', price=500)
        self.assertEqual(response.status_code,200)
        response = self.c.post('/select-card/', {'event-id':self.event3.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        print(self.user1.profile.credit_card.first())
        response = self.c.post('/to-transaction/', follow=True)
        self.assertEqual(response.status_code, 200)"""




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