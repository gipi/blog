from django_comments.forms import CommentForm
from math_captcha.forms import MathCaptchaForm

from captcha_comment.models import CaptchaComment

class CaptchaFormComment(CommentForm, MathCaptchaForm):
    pass
