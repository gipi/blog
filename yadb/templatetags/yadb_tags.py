# http://en.gravatar.com/site/implement/python
# import code for encoding urls and generating md5 hashes
from django import template
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.functional import allow_lazy
from django.utils.encoding import force_unicode

import urllib, hashlib
import re


register = template.Library()

@register.inclusion_tag('gravatar.html')
def gravatar(email):
    size = 40

    # construct the url
    gravatar_url = "http://www.gravatar.com/avatar.php?"
    gravatar_url += urllib.urlencode({
        'gravatar_id':hashlib.md5(email).hexdigest(),
        'size':str(size)}
    )

    return { 'url': gravatar_url }

@register.inclusion_tag('comments/entry_skeleton.html')
def comment_entry(comment):
    return {
        'username': comment.user_name,
        'email': comment.user_email,
        'site': comment.user_url,
        'content': comment.comment,
        'date': comment.submit_date,
    }


"""
This function is a modified version of truncate_html_words which you can
found in django/utils/text.
"""
def truncate_html_words_ng(s, num, ellipsis):
    """
    Truncates html to a certain number of words (not counting tags and
    comments). Closes opened tags if they were correctly closed in the given
    html.
    """
    s = force_unicode(s)
    length = int(num)
    if length <= 0:
        return u''
    html4_singlets = ('br', 'col', 'link', 'base', 'img', 'param', 'area', 'hr', 'input')
    # Set up regular expressions
    re_words = re.compile(r'&.*?;|<.*?>|(\w[\w-]*)', re.U)
    re_tag = re.compile(r'<(/)?([^ ]+?)(?: (/)| .*?)?>')
    # Count non-HTML words and keep note of open tags
    pos = 0
    ellipsis_pos = 0
    words = 0
    open_tags = []
    while words <= length:
        m = re_words.search(s, pos)
        if not m:
            # Checked through whole string
            break
        pos = m.end(0)
        if m.group(1):
            # It's an actual non-HTML word
            words += 1
            if words == length:
                ellipsis_pos = pos
            continue
        # Check for tag
        tag = re_tag.match(m.group(0))
        if not tag or ellipsis_pos:
            # Don't worry about non tags or tags after our truncate point
            continue
        closing_tag, tagname, self_closing = tag.groups()
        tagname = tagname.lower()  # Element names are always case-insensitive
        if self_closing or tagname in html4_singlets:
            pass
        elif closing_tag:
            # Check for match in open tags list
            try:
                i = open_tags.index(tagname)
            except ValueError:
                pass
            else:
                # SGML: An end tag closes, back to the matching start tag, all unclosed intervening start tags with omitted end tags
                open_tags = open_tags[i+1:]
        else:
            # Add it to the start of the open tags list
            open_tags.insert(0, tagname)

    # END OF WHILE
    if words <= length:
        # Don't try to close tags if we don't need to truncate
        return s
    out = s[:ellipsis_pos] + ' ...'
    # Close any tags still open
    for tag in open_tags:
        out += '</%s>' % tag
    # Return string
    return out + ellipsis
truncate_html_words_ng = allow_lazy(truncate_html_words_ng, unicode)

def truncatewords_html_and_more(value, args):
    truncate_value = truncate_html_words_ng(value,
            settings.PREVIEW_POST_LENGTH,
            '<a href="%s">(leggi tutto)</a>' % \
                    reverse('blog-post', args=[args.slug]))

    return truncate_value

truncatewords_html_and_more.is_safe = True
register.filter('truncatewords_html_and_more', truncatewords_html_and_more)

@register.tag(name='restructuredTextWO')
def restructured_text_without(parser, token):
    """
    Allow to delete a registered role from the restructuredtext
    filter so to avoid unwanted side effects. For example I don't
    want to allow latex directive in comment.
    """
    nodelist = parser.parse(('endrestructuredTextWO',))
    parser.delete_first_token()

    try:
        args = token.split_contents()
        if len(args) == 1:
            raise ValueError

    except ValueError:
        raise template.TemplateSyntaxError(
                '%r tag requires at least an argument' % token.contents.split()[0])

    tag_name = args.pop(0)

    return Without(nodelist, args)



class Without(template.Node):
    def __init__(self, nodelist, rst_names):
        if settings.DEBUG:
            print 'Without', rst_names

        self.nodelist = nodelist
        self.rst_names = rst_names
        self.roles = {}
        self.directives = {}

    def render(self, context):
        from docutils.parsers.rst import roles, directives

        for name in self.rst_names:
            if roles._role_registry.has_key(name):
                role_fn1 = roles._role_registry.pop(name, None)
                # I don't know why but also this has to be pop'd (maybe cache)
                role_fn2 = roles._roles.pop(name, None)
                print 'r1, r2', role_fn1, role_fn2
                self.roles[name] = (role_fn1, role_fn2)

            if directives._directives.has_key(name):
                print '****** directive'
                directive_fn1 = None#directives._directive_registry.pop(name)
                directive_fn2 = directives._directives.pop(name)
                self.directives[name] = (directive_fn1, directive_fn2)

        output = self.nodelist.render(context)

        # restore the roles and directives
        for name, (fn1, fn2) in self.roles.items():
            if fn1:
                roles._role_registry[name] = fn1
            if fn2:
                roles._roles[name] = fn2

        for name, (fn1, fn2) in self.directives.items():
            # I don't know if this works like roles
            #if fn1:
            #    directives._directive_registry[name] = fn1
            if fn2:
                directives._directives[name] = fn2

        return output
