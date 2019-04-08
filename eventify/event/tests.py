from django.test import TestCase, RequestFactory, Client
from .models import Post
from .forms import UploadFileForm
from .urls import urlpatterns
from django.contrib.auth.models import User
from django.urls import resolve
from django.urls import reverse


# Create your tests here.
class FormsTestCase(TestCase):
    def test_valid_form(self):
        form_data = {'something'}
        form = UploadFileForm(data=form_data)
        self.assertTrue(form.is_valid())


""" Ikke verdt å teste
class UrlsTestCase(TestCase):
    def test_reverse(self):
        url = reverse('user', args=['axel_kjonsberg'])
        self.assertEqual(url, '/user/axel_kjonsberg/')

    def test_resolve(self):
        resolver = resolve('/events/')
        self.assertEqual(resolver.view_name, 'events')
"""


# Integration test of Event's functionality from the users "view"
class TestEvent(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='Ole', email='ole@mail.no', password='oletest123')
        self.user2 = User.objects.create_user(username='Sjur', email='sjur@mail.no', password='sjurtest123')
        self.c = Client(HTTP_USER_AGENT='Mozilla/5.0')

    def test__view_denies_anonymous(self):
        response = self.c.get('/event/join/', follow=True)
        self.assertRedirects(response, '/login/')

    def test_call_view_loads(self):
        self.c.login(username='Ole', password='oletest123')
        response = self.c.get('/event/join/')
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
        self.assertEqual(self.event1.author, 'Ole')
        self.assertEqual(self.event2.author, 'Sjur')


    """ Disse flyttes til TestEvent
        def test_join_event(self):
            self.assertTrue(self.user1 in self.event2.attendees().all())
            self.assertTrue(self.user2 in self.event1.attendees().all())
    
        def test_leave_event(self):
            self.user1.eventLeave(self.event2)
            self.user2.eventLeave(self.event1)
            self.assertTrue(self.user1 not in self.event2.attendees().all())
            self.assertTrue(self.user2 not in self.event1.attendees().all())
    """

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
