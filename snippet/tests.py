# REGRESSIONI
#  1. chdir on texrender come back on error
#  2. rmdir tmpdir
from django.test import TestCase
from django.core.urlresolvers import reverse

from snippet.models import Blog
from snippet.utils import slugify

class RenderingTest(TestCase):
    fixtures = ['auth_data.json']
    def test_tex(self):
        content = r"""
        .. latex::
        F_{\mu\nu} = \partial_\mu A_\nu - \partial_\nu A_\mu
        """
        self.client.login(username='test', password='password')
        response = self.client.post('/preview/',
            {'content': content},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)

class BlogTests(TestCase):
    fixtures = ['auth_data.json', 'blog-data.json',]
    def test_blog_add(self):
        # the page exists
        self.client.login(username='test', password='password')
        response = self.client.get(reverse('blog-add'))
        self.assertEqual(response.status_code, 200)

        previous_n = len(Blog.objects.all())

        # some errors
        response = self.client.post(reverse('blog-add'), {
            'content': 'this is a content',
            'tags': 'love, lulz' }
        )
        self.assertFormError(response, 'form', 'title',
                [u'This field is required.'])
        #self.assertRedirects(response, '/blog/')

        # can I submit without error
        response = self.client.post(reverse('blog-add'),
                {
                'title': 'This is a test',
                'content': 'this is a content',
                'tags': 'love, lulz',
                'status': 'pubblicato',
                })
        #self.assertRedirects(response, '/blog/')
        self.assertEqual(len(Blog.objects.all()), previous_n + 1)

    def test_blog_list_with_bozza(self):
        url = reverse('blog-list')
        response = self.client.get(url)
        print response.context[0]['blogs']
        self.assertEqual(len(response.context[0]['blogs']), 1)

    def test_blog_view_bozza_when_logged(self):
        url = reverse('blog-list')

        # first check there are only published
        response = self.client.get(url)
        self.assertEqual(len(response.context[0]['blogs']), 1)

        # second check for unpublished when you are logged
        self.client.login(username='test', password='password')
        response = self.client.get(url)
        self.assertEqual(len(response.context[0]['blogs']), 2)

class AuthTest(TestCase):
    fixtures = ['auth_data.json']
    def test_login(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('login'),
                {'username': 'test', 'password': 'password'})
        self.assertRedirects(response, reverse('home'))

    def test_logout(self):
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 200)

    def test_blog_add(self):
        response = self.client.get(reverse('blog-add'))
        self.assertRedirects(response,
                '/login/?next=' + reverse('blog-add'))

    def test_preview(self):
        # in order to preview need to login
        response = self.client.get('/preview/')
        self.assertRedirects(response, '/login/?next=/preview/')

        response = self.client.post('/preview/', {'content': 'miao'})
        self.assertRedirects(response, '/login/?next=/preview/')

        # need XMLHttpRequest
        self.client.login(username='test', password='password')
        response = self.client.get('/preview/')
        self.assertEqual(response.status_code, 400)

        response = self.client.post('/preview/',
                {'content': 'miao'})
        self.assertEqual(response.status_code, 400)

        # so we use it
        response = self.client.post('/preview/',
                {'content': 'miao'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)

class UtilTests(TestCase):
    def test_slugify(self):
        slug = slugify('l\'amore non ESISTE')
        self.assertEqual(slug, 'l-amore-non-esiste')

class FeedsTests(TestCase):
    fixtures = ['auth_data.json', 'blog-data.json',]
    def test_existence(self):
        response = self.client.get('/feeds/latest/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'snippet/feeds_title.html')
        self.assertTemplateUsed(response, 'snippet/feeds_description.html')

        # check for user realated feeds
        response = self.client.get('/feeds/user/test/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Blog object')

        # TODO: check for a precise number of posts
