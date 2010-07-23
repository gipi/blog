from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.http import SimpleCookie
from django.core.exceptions import ObjectDoesNotExist

from django_stats.models import Stats, StatsSession

class StatsTests(TestCase):
    page_to_test = reverse('blog-post',
            args=['superfici-minimali-e-bolle-di-sapone',])
    """
    Remember: testclient uses a session field read only so
    we have to delete session using cookies related method.
    """
    fixtures = ['blog-data.json', 'session.json']
    def test_session(self):
        """check strange behaviour of testclient"""
        response = self.client.get(self.page_to_test)
        old_session_key = self.client.session.session_key

        response = self.client.get(self.page_to_test)
        new_session_key = self.client.session.session_key

        response = self.client.get(self.page_to_test)
        real_new_session_key = self.client.session.session_key

        self.assertNotEqual(new_session_key, old_session_key)
        self.assertEqual(real_new_session_key, new_session_key)

    def test_page_counter_increment(self):
        base_counter = Stats.objects.get(page_path=self.page_to_test)

        response = self.client.get(self.page_to_test)

        s = Stats.objects.get(page_path=self.page_to_test)
        old_counter = s.counter

        self.assertEqual(old_counter, base_counter.counter + 1)

        response = self.client.get(self.page_to_test)

        s = Stats.objects.get(page_path=self.page_to_test)
        new_counter = s.counter

        # second not increment (same session)
        self.assertEqual(new_counter, old_counter + 1)

        # again and again
        old_counter = new_counter

        response = self.client.get(self.page_to_test)

        s = Stats.objects.get(page_path=self.page_to_test)
        new_counter = s.counter

        # second not increment (same session)
        self.assertEqual(new_counter, old_counter)

    def test_page_counter_increment_with_user_agent(self):
        base_counter = Stats.objects.get(page_path=self.page_to_test)

        response = self.client.get(self.page_to_test, {},
                HTTP_USER_AGENT='test-client')
        s = Stats.objects.get(page_path=self.page_to_test)

        old_counter = s.counter
        # first access increment counter
        self.assertEqual(old_counter, base_counter.counter + 1)

        response = self.client.get(self.page_to_test, {},
                HTTP_USER_AGENT='test-client')

        s = Stats.objects.get(page_path=self.page_to_test)
        new_counter = s.counter
        # second not increment (same session)
        self.assertEqual(new_counter, old_counter + 1)

        old_counter = new_counter
        response = self.client.get(self.page_to_test, {},
                HTTP_USER_AGENT='test-client')

        s = Stats.objects.get(page_path=self.page_to_test)
        new_counter = s.counter
        # second not increment (same session)
        self.assertEqual(new_counter, old_counter)
