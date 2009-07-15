# REGRESSIONI
#  1. chdir on texrender come back on error
#  2. rmdir tmpdir
from django.test import TestCase

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
	fixtures = ['auth_data.json']
	def test_blog_add(self):
		# the page exists
		self.client.login(username='test', password='password')
		response = self.client.get('/blog/add/')
		self.assertEqual(response.status_code, 200)

		# can I submit without error
		response = self.client.post('/blog/add',
			{
				'title': 'This is a test',
				'content': 'this is a content',
				'tags': 'love, lulz'
			})
		#self.assertRedirects(response, '/blog/')
		self.assertEqual(len(Blog.objects.all()), 1)

class AuthTest(TestCase):
	fixtures = ['auth_data.json']
	def test_login(self):
		response = self.client.get('/login/')
		self.assertEqual(response.status_code, 200)

		response = self.client.post('/login/',
				{'username': 'test', 'password': 'password'})
		self.assertRedirects(response, '/')

	def test_logout(self):
		response = self.client.get('/logout/')
		self.assertEqual(response.status_code, 200)
	
	def test_blog_add(self):
		response = self.client.get('/blog/add/')
		self.assertEqual(response.status_code, 403)

class UtilTests(TestCase):
	def test_slugify(self):
		slug = slugify('l\'amore non ESISTE')
		self.assertEqual(slug, 'l-amore-non-esiste')
