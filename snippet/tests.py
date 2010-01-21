# REGRESSIONI
#  1. chdir on texrender come back on error
#  2. rmdir tmpdir
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.conf import settings

from snippet.models import Blog
from snippet.utils import slugify

import os

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

    def test_blog_order(self):
        self.client.login(username='test', password='password')
        url = reverse('blog-list')
        response = self.client.get(url)
        blogs = response.context[0]['blogs']
        self.assertEqual(blogs[0].creation_date > blogs[1].creation_date, True)

    def _get_uploaded_file_name(self):
        return settings.UPLOAD_PATH + os.path.basename(__file__)

    def _upload_my_self(self):
        url = reverse('blog-upload')

        # then open THIS file
        filez = open(__file__, 'r')

        post_data = {
            'file': filez,
        }
        response = self.client.post(url, post_data)
        filez.close()

        uploaded_file = self._get_uploaded_file_name()
        self.assertEqual(os.stat(uploaded_file) != None, True)

        return response

    def test_upload(self):
        #   1. the file is being uploaded
        self.client.login(username='test', password='password')

        response = self._upload_my_self()
        self.assertRedirects(response, reverse('blog-list'))

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

    def test_upload(self):
        response = self.client.get(reverse('blog-upload'))
        self.assertRedirects(response,
                '/login/?next=' + reverse('blog-upload'))

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
