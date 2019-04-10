from django.test import TestCase, Client
from django.contrib.auth.models import User
from event.models import Post

class ViewsTestCase(TestCase):
    def setUp(self):
        print("Setting up: UserTestCase")
        self.user1 = User.objects.create_user(username='ole', email='ole@mail.no', password='ole123')
        self.user2 = User.objects.create_user(username='sjur', email='sjur@mail.no', password='sjur123')
        self.user3 = User.objects.create_user(username='victor', email='victor@mail.no', password='victor123')
        self.event1 = Post.objects.create(title='Strikkekveld', author=self.user3, location='Trondheim',
                                          content='Syk strikkekveld i Trondheim')
        self.c = Client()

    def test_add_contact(self):
        self.c.login(username='ole', password='ole123')
        response = self.c.post('/add-friend/', {'user-id': self.user2.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user1 in self.user2.profile.requests.all())
        self.assertTrue(self.user2 in self.user1.profile.sent_requests.all())

    def test_accept_reject_request(self):
        self.c.login(username='ole', password='ole123')
        response = self.c.post('/add-friend/', {'user-id': self.user2.id}, follow=True)
        self.c.logout()
        self.c.login(username='victor', password='victor123')
        response = self.c.post('/add-friend/', {'user-id': self.user2.id}, follow=True)
        self.c.logout()
        self.c.login(username='sjur', password='sjur123')
        response = self.c.post('/requests/', follow=True)
        self.assertEqual(response.status_code, 200)
        response = self.c.post('/accept-friend/', {'user-id': self.user1.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user1 in self.user2.profile.contacts.all())
        response = self.c.post('/decline-friend/', {'user-id': self.user3.id}, follow=True)
        self.assertTrue(self.user3 not in self.user2.profile.contacts.all())
        self.assertTrue(self.user2 not in self.user2.profile.sent_requests.all())

    def test_cancel_request(self):
        self.c.login(username='ole', password='ole123')
        response = self.c.post('/add-friend/', {'user-id': self.user2.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user1 in self.user2.profile.requests.all())
        response = self.c.post('/cancel-request/', {'user-id': self.user2.id}, follow=True)
        self.assertTrue(self.user1 not in self.user2.profile.requests.all())
        self.assertTrue(self.user2 not in self.user1.profile.sent_requests.all())

    def test_remove_contact(self):
        self.c.login(username='ole', password='ole123')
        response = self.c.post('/add-friend/', {'user-id': self.user2.id}, follow=True)
        self.c.logout()
        self.c.login(username='sjur', password='sjur123')
        response = self.c.post('/accept-friend/', {'user-id': self.user1.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        response = self.c.post('/remove-contact/', {'user-id': self.user1.id}, follow=True)
        self.assertTrue(self.user1 not in self.user2.profile.contacts.all())
        self.assertTrue(self.user2 not in self.user1.profile.contacts.all())

    def test_get_friend(self):
        self.c.login(username='ole', password='ole123')
        response = self.c.post('/contacts/', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_search_user(self):
        self.c.login(username='ole', password='ole123')
        response = self.c.post('/user-search/', {'search-field': 'sjur'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user2 in response.context['users'])

    def test_search_user_event(self):
        self.c.login(username='ole', password='ole123')
        response = self.c.post('/event/join/', {'event-id': self.event1.id}, follow=True)
        self.assertTrue(self.user1 in self.event1.attendees.all())
        self.c.logout()
        self.c.login(username='sjur', password='sjur123')
        response = self.c.post('/user-search-event/', {'search-field': 'ole', 'event-id': self.event1.id}, follow=True)
        self.assertTrue(self.user1 in response.context['attending'])

    def test_register_credit_card(self):
        self.c.login(username='ole', password='ole123')
        response = self.c.post('/register-card/', {
            'card_number': '1234567887654321',
            'security_code': '123',
            'expiration_month': '12',
            'expiration_year': '22',
            'amount': 10000
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user1.profile.credit_card.all().count(), 1)
        response = self.c.post('/register-card/', {
            'card_number': '12345678854321',
            'security_code': '123',
            'expiration_month': '12',
            'expiration_year': '22',
            'amount': 10000
        }, follow=True)
        self.assertEqual(self.user1.profile.credit_card.all().count(), 1)
        response = self.c.post('/register-card/', {
            'card_number': '1234567887654321',
            'security_code': '12',
            'expiration_month': '12',
            'expiration_year': '22',
            'amount': 10000
        }, follow=True)
        response = self.c.post('/register-card/', {
            'card_number': '1234567887654321',
            'security_code': '123',
            'expiration_month': '1',
            'expiration_year': '22',
            'amount': 10000
        }, follow=True)
        response = self.c.post('/register-card/', {
            'card_number': '1234567887654321',
            'security_code': '123',
            'expiration_month': '12',
            'expiration_year': '18',
            'amount': 10000
        }, follow=True)
        response = self.c.post('/register-card/', {
            'card_number': '1234567887654321',
            'security_code': '123',
            'expiration_month': '12',
            'expiration_year': '22',
            'amount': -10000
        }, follow=True)
        self.assertEqual(self.user1.profile.credit_card.all().count(), 1)
        response = self.c.get('/register-card/', {
            'card_number': '1234567887654321',
            'security_code': '123',
            'expiration_month': '12',
            'expiration_year': '18',
            'amount': 10000
        }, follow=True)
        response = self.c.post('/get-cards/', follow=True)
        self.assertQuerysetEqual(response.context['cards'], self.user1.profile.credit_card.all(), transform=lambda x: x)

    def test_change_on_contact(self):
        self.c.login(username='ole', password='ole123')
        response = self.c.post('/add-friend/', {'user-id': self.user2.id}, follow=True)
        self.c.logout()
        self.c.login(username='sjur', password='sjur123')
        self.assertEqual(self.user2.profile.notifications.all().count(), 1)
        response = self.c.post('/change-on-contact/', follow=True)
        self.user2.refresh_from_db()
        self.assertFalse(self.user2.profile.on_contact)
        self.c.logout()
        self.c.login(username='victor', password='victor123')
        response = self.c.post('/add-friend/', {'user-id': self.user2.id}, follow=True)
        self.c.logout()
        self.c.login(username='sjur', password='sjur123')
        self.assertEqual(self.user2.profile.notifications.all().count(), 1)
        response = self.c.post('/change-on-contact/', follow=True)
        self.user2.refresh_from_db()
        self.assertTrue(self.user2.profile.on_contact)

    def test_change_event_invite(self):
        self.c.login(username='sjur', password='sjur123')
        response = self.c.post('/change-event-invite/', follow=True)
        self.user2.refresh_from_db()
        self.assertFalse(self.user2.profile.on_event_invite)
        response = self.c.post('/change-event-invite/', follow=True)
        self.user2.refresh_from_db()
        self.assertTrue(self.user2.profile.on_event_invite)

    def test_change_on_event_update_delete(self):
        self.c.login(username='sjur', password='sjur123')
        response = self.c.post('/change-on-event-update-delete/', follow=True)
        self.user2.refresh_from_db()
        self.assertFalse(self.user2.profile.on_event_update_delete)
        response = self.c.post('/change-on-event-update-delete/', follow=True)
        self.user2.refresh_from_db()
        self.assertTrue(self.user2.profile.on_event_update_delete)

    def test_change_on_event_host(self):
        self.c.login(username='sjur', password='sjur123')
        response = self.c.post('/change-on-event-host/', follow=True)
        self.user2.refresh_from_db()
        self.assertFalse(self.user2.profile.on_event_host)
        response = self.c.post('/change-on-event-host/', follow=True)
        self.user2.refresh_from_db()
        self.assertTrue(self.user2.profile.on_event_host)

    def test_to_notifications(self):
        self.c.login(username='sjur', password='sjur123')
        response = self.c.post('/edit-notifications/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user2.id, response.context['user'].id)

    def test_delete_notification(self):
        self.c.login(username='ole', password='ole123')
        response = self.c.post('/add-friend/', {'user-id': self.user2.id}, follow=True)
        self.c.logout()
        self.c.login(username='sjur', password='sjur123')
        self.assertEqual(self.user2.profile.notifications.all().count(), 1)
        response = self.c.post('/delete-notifications/', follow=True)
        self.user2.refresh_from_db()
        self.assertEqual(self.user2.profile.notifications.all().count(), 0)

    def test_event_invites(self):
        self.c.login(username='ole', password='ole123')
        response = self.c.post('/invites/', follow=True)
        self.assertEqual(response.status_code, 200)









