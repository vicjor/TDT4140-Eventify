from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import User

from users.models import Notification, Credit
from event.models import Post


# Integration test of Event's functionality from the users "view"
class TestEvent(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='ole', email='ole@mail.no', password='oletest123')
        self.user2 = User.objects.create_user(username='sjur', email='sjur@mail.no', password='sjurtest123')
        self.user3 = User.objects.create_superuser(username='victor', email='victor@mail.no', password='victor123')
        self.event1 = Post.objects.create(title='Strikkekveld', author=self.user1, location='Trondheim',
                                          content='Syk strikkekveld i Trondheim', id=123)
        self.event2 = Post.objects.create(title='Sykveld', author=self.user2, location='Oslo',
                                          content='Sykveld i hovedstaden', id=124)
        self.event3 = Post.objects.create(title='Fest', author=self.user3, location='Trondheim',
                                          content='Fest i Trondheim', is_private=True, id=1)
        self.event4 = Post.objects.create(title='Party', author=self.user3, location='Stavanger',
                                          content='Fest i Stavanger', price=2000)
        self.event5 = Post.objects.create(title='Venteliste', author=self.user3, location='Oslo',
                                          content='Test av venteliste', attendance_limit=1, waiting_list_limit=10)
        self.c = Client()

    def test_join_event_denies_anonymous(self):
        response = self.c.post('/event/join/', follow=True)
        self.assertRedirects(response, '/login/?next=/event/join/')

    def test_join_and_leave_event(self):
        self.c.login(username='ole', password='oletest123')
        self.c.post('/event/join/', {'event-id': self.event2.id}, follow=True)
        self.assertEqual(self.event2.attendees.count(), 1)
        self.assertTrue(self.user1 in self.event2.attendees.all())
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
        self.assertEqual(Post.objects.get(pk=3).count(),1)
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
        self.c.post('/add-host/', {'event-id': self.event1.id, 'user-id': self.user2.id}, follow=True)
        self.assertEqual(self.event1.co_authors.count(), 1)
        response = self.c.post('/remove-host/', {'event-id': self.event1.id, 'user-id': self.user2.id}, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_remove_attendee(self):
        self.c.login(username='sjur', password='sjurtest123')
        self.c.post('/event/join/', {'event-id': self.event1.id}, follow=True)
        self.c.logout()
        self.c.login(username='ole', password='oletest123')
        response = self.c.post('/remove-attendee/', {'event-id': self.event1.id, 'user-id':self.user2.id}, follow = True)
        self.assertEqual(response.status_code, 200)

    def test_event_created(self):
        self.c.login(username='ole', password='oletest123')
        response = self.c.get('/event/created/')
        self.assertEqual(response.status_code, 200)

    def test_my_events(self):
        self.c.login(username='victor', password='victor123')
        self.c.post('/event/join/', {'event-id': self.event2.id}, follow=True)
        response = self.c.post('/my-events/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.event2 in response.context['joined_events'])

    def test_private_event_remove_attendee(self):
        self.c.login(username='victor', password='victor123')
        self.c.post('/send-invite/', {'event-id': self.event3.id, 'user-id': self.user2.id}, follow=True)
        self.c.logout()
        self.c.login(username='sjur', password='sjurtest123')
        self.c.post('/event/join/', {'event-id': self.event3.id}, follow=True)
        self.assertTrue(self.user2 in self.event3.attendees.all())
        self.c.logout()
        self.c.login(username='victor', password='victor123')
        response = self.c.post('/remove-attendee/', {'event-id': self.event3.id, 'user-id': self.user2.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user2 not in self.event3.attendees.all())
        self.c.login(username='sjur', password='sjurtest123')
        self.assertEqual(self.user2.profile.notifications.count(), 2)

    def test_private_event_leave_event(self):
        self.c.login(username='victor', password='victor123')
        self.c.post('/send-invite/', {'event-id': self.event3.id, 'user-id': self.user2.id}, follow=True)
        self.c.logout()
        self.c.login(username='sjur', password='sjurtest123')
        self.c.post('/event/join/', {'event-id': self.event3.id}, follow=True)
        self.assertTrue(self.user2 in self.event3.attendees.all())
        self.c.post('/event/leave/', {'event-id': self.event3.id}, follow=True)
        self.assertEqual(self.event2.attendees.count(), 0)

    def test_private_event_decline_invitation(self):
        self.c.login(username='victor', password='victor123')
        self.c.post('/send-invite/', {'event-id': self.event3.id, 'user-id': self.user2.id}, follow=True)
        self.c.logout()
        self.c.login(username='sjur', password='sjurtest123')
        self.assertTrue(self.user2 in self.event3.invited.all())
        self.c.post('/decline-invite/', {'event-id': self.event3.id}, follow=True)
        self.assertFalse(self.user2 in self.event3.invited.all())
        self.assertFalse(self.user2 in self.event3.attendees.all())


    def test_waiting_list(self):
        self.c.login(username='ole', password='oletest123')
        self.c.post('/event/join/', {'event-id': self.event5.id}, follow=True)
        self.c.logout()
        self.c.login(username='sjur', password='sjurtest123')
        self.c.post('/event/join/', {'event-id': self.event5.id}, follow=True)
        self.event5.refresh_from_db()
        self.assertEqual(self.event5.attendees.count(), 1)
        self.assertEqual(self.event5.waiting_list.count(), 1)
        self.assertTrue(self.user2 in self.event5.waiting_list.all())

    def test_leave_waiting_list(self):
        self.c.login(username='ole', password='oletest123')
        self.c.post('/event/join/', {'event-id': self.event5.id}, follow=True)
        self.c.post('leave-waiting-list/', {'event-id': self.event5.id}, follow=True)
        self.c.logout()
        self.c.login(username='sjur', password='sjurtest123')
        self.c.post('/event/join/', {'event-id': self.event5.id}, follow=True)
        self.event5.refresh_from_db()
        self.assertTrue(self.user2 in self.event5.waiting_list.all())
        self.c.post('/leave-waiting-list/', {'event-id': self.event5.id}, follow=True)
        self.event5.refresh_from_db()
        self.assertFalse(self.user2 in self.event5.waiting_list.all())
        self.assertEqual(self.event5.waiting_list.count(), 0)

    def test_join_event_from_waiting_list(self):
        self.c.login(username='ole', password='oletest123')
        self.c.post('/event/join/', {'event-id': self.event5.id}, follow=True)
        self.c.post('leave-waiting-list/', {'event-id': self.event5.id}, follow=True)
        self.c.logout()
        self.c.login(username='sjur', password='sjurtest123')
        self.c.post('/event/join/', {'event-id': self.event5.id}, follow=True)
        self.event5.refresh_from_db()
        self.assertTrue(self.user2 in self.event5.waiting_list.all())
        self.c.logout()
        self.c.login(username='ole', password='oletest123')
        self.c.post('/event/leave/', {'event-id': self.event5.id}, follow=True)
        self.assertTrue(self.user2 in self.event5.attendees.all())
        self.assertTrue(self.user2 not in self.event5.waiting_list.all())

    def test_search_events(self):
        response = self.c.post('/events/search/', {'event-search': 'Strikkekveld', 'location-search': 'Trondheim'},
                               follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['events']), 1)
        response = self.c.post('/events/search/', {'event-search': '', 'location-search': 'Trondheim'},
                               follow=True)
        self.assertTrue(len(response.context['events']), 2)
        self.assertTrue(self.event3 in response.context['events'])

    def test_add_card_and_pay(self):
        self.c.login(username='ole', password='oletest123')
        self.c.post('/register-card/', {
            'card_number': '1234567887654321',
            'security_code': '123',
            'expiration_month': '12',
            'expiration_year': '20',
            'amount': 5000}, follow=True)
        self.assertEqual(self.user1.profile.credit_card.all().first().amount, 5000)
        self.assertTrue(self.user1.profile.credit_card.count() == 1)
        self.c.post('/select-card/', {'event-id': self.event4.id}, follow=True)

        response = self.c.post('/confirm-card/', {
            'event-id': self.event4.id,
            'card-id': self.user1.profile.credit_card.all().first().id
        }, follow=True)
        self.assertTrue(response.context['card'].id == self.user1.profile.credit_card.all().first().id)
        self.user1.refresh_from_db()
        self.c.post('/execute-transaction/', {
            'event-id': self.event4.id,
            'card-id': self.user1.profile.credit_card.first().id
        }, follow=True)
        self.assertTrue(self.user1 in self.event4.attendees.all())
        self.assertEqual(self.user1.profile.credit_card.all().first().amount, 3000)

    """def test_notification_redirections(self):
        self.c.login(username='sjur', password='sjurtest123')
        self.not1 = Notification.objects.create(user=self.user2, event=self.event3,
                                                text="Invited", type='event', id=1)
        self.not2 = Notification.objects.create(user=self.user2, event=self.event3,
                                                text="Home", type='home', id=2)
        self.not3 = Notification.objects.create(user=self.user2, event=self.event3,
                                                text="Person joined", type='person_joined', id=3)
        self.not4 = Notification.objects.create(user=self.user2, event=self.event3,
                                                text="New request", type='new_request', id=4)
        self.not5 = Notification.objects.create(user=self.user2, event=self.event3,
                                                text="Profile", type='profile', id=5)
        response = self.c.post('handle-notification/1', {'notification_id': self.not1.id}, follow=True)
        self.assertRedirects(response, '/event/1/')

    def test_call_view_fails_blank(self):
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