# REGRESSIONI
#  1. chdir on texrender come back on error
#  2. rmdir tmpdir
from django.test import TestCase

class RenderingTest(TestCase):
	def test_tex(self):
		content = r"""
		.. latex::
		 F_{\mu\nu} = \partial_\mu A_\nu - \partial_\nu A_\mu
		"""
		response = self.client.post('/entry/',
				{'content': content})
		self.assertEqual(response.status_code, 200)

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
