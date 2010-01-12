# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from snippet.forms import EntryForm, BlogForm
from snippet import rst_tex, rst_code
from snippet.utils import slugify
from snippet.models import Blog
from snippet.decorators import superuser_only, ajax_required

example = """
u

Twitter per programmatori e scienziati
======================================

Ecco un esempio di codice TeX

.. latex::
 A = \pmatrix{
   a & b \cr
   c & d \cr
  }\quad\det(A - \lambda I) =
 \left|\matrix{
 a - \lambda & b \cr
 c           & d -\lambda \cr
 }\\right| = \lambda^2 - \hbox{tr}(A)\lambda + \det(A)

ma anche di capacita` grafiche senza pari

.. tikz::
 [scale=0.5]
 \draw (0,0) -- (90:1cm) arc (90:360:1cm) arc (0:30:1cm) -- cycle;
 \draw (60:5pt) -- +(30:1cm) arc (30:90:1cm) -- cycle;
 \draw (3,0)  +(0:1cm) -- +(72:1cm) -- +(144:1cm) -- +(216:1cm) --
           +(288:1cm) -- cycle;

ma mica finisce cosi`, c'e` anche roba per coder

.. code-block:: python

    if request.is_ajax():
        return render_to_response('restructured_text.html',
                {'content':formula},
                context_instance=RequestContext(request))
"""

@login_required
def preview(request):
    """
    This function get only a POST with content variable and return
    a preview of the post.
    """
    if request.is_ajax():
        return render_to_response('restructured_text.html',
                {'content':request.POST['content']},
                context_instance=RequestContext(request))
    else:
    	return HttpResponseBadRequest('NONONONO')

    if request.is_ajax():
        return render_to_response('restructured_text.html',
                {'content':formula},
                context_instance=RequestContext(request))

    return render_to_response('homepage.html',
            {'form': form, 'entry':formula},
            context_instance=RequestContext(request))

def blog_list(request):
	return render_to_response('snippet/blog_list.html',
			{'blogs': Blog.objects.filter(status='pubblicato')},
			context_instance=RequestContext(request))

def blog_view(request, slug):
	form = None
	content = None
	blog = get_object_or_404(Blog, slug=slug)

	return render_to_response('snippet/blog.html', {'blog': blog},
			context_instance=RequestContext(request))

@login_required
def blog_add(request, id=None):
	instance = None
	if id:
		instance = get_object_or_404(Blog, pk=id)

	if request.method == 'POST':
		form = BlogForm(request.POST, instance=instance)
		if form.is_valid():
			blog = form.save(commit=False)
			blog.slug = slugify(blog.title)
			blog.user = request.user
			blog.save()
			return HttpResponseRedirect('/blog/')
	else:
		form = BlogForm(instance=instance)

	return render_to_response('snippet/blog.html', {'form': form},
			context_instance=RequestContext(request))
