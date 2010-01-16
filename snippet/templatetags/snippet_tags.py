# http://en.gravatar.com/site/implement/python
# import code for encoding urls and generating md5 hashes
import urllib, hashlib
from django import template

register = template.Library()


@register.inclusion_tag('gravatar.html')
def gravatar(email, site):
    size = 40

    # construct the url
    gravatar_url = "http://www.gravatar.com/avatar.php?"
    gravatar_url += urllib.urlencode({
        'gravatar_id':hashlib.md5(email).hexdigest(),
        'default':site, 'size':str(size)}
    )

    return { 'url': gravatar_url }

@register.inclusion_tag('entry_skeleton.html')
def entry(username, email, content, creation_date):
    return {
        'username': username,
        'email': email,
        'content': content,
        'date': creation_date
    }
