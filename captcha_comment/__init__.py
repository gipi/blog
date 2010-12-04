"""
Custom Comment application to allow captcha system.

Some hint from <http://stackoverflow.com/questions/3864868/django-adding-simple-captcha-to-django-comments>
"""
from captcha_comment.forms import CaptchaFormComment

def get_form():
    return CaptchaFormComment
