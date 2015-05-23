# encoding utf-8
'''
Simple context processor that adds the ``site`` variable to the template.

In the future maybe add all the variables and attributes listed `here <http://jekyllrb.com/docs/variables/#global-variables>`_.
'''
class Site(object):
    def __init__(self, name, base_url):
        self.title = name
        self.baseurl = base_url
        self.description = u'Yet Another Django Blog'

def liquid(request):
    return {
        'site': Site('YADB', '/blog/'),
    }