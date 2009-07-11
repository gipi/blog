# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.conf import settings
from django.http import HttpResponseRedirect

from snippet.forms import EntryForm, BlogForm

from snippet import rst_tex, rst_code

from snippet.models import Blog

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

def test(request):
    formula = ""
    if request.method != 'POST':
        form = EntryForm(initial={'content': example})
    else:
        form = EntryForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
	    formula = instance.content
	    # d41d8cd98f00b204e9800998ecf8427e = la stringa vuota
	    print 'formula: ', formula

    if request.is_ajax():
        return render_to_response('restructured_text.html',
                {'content':formula},
                context_instance=RequestContext(request))

    return render_to_response('homepage.html',
            {'form': form, 'entry':formula},
            context_instance=RequestContext(request))

def blog_list(request):
	return render_to_response('snippet/blog_list.html',
			{'blogs': Blog.objects.all()},
			context_instance=RequestContext(request))

def blog_view(request, slug):
	form = None
	content = None
	blog = get_object_or_404(Blog, slug=slug)

	return render_to_response('snippet/blog.html', {'blog': blog},
			context_instance=RequestContext(request))

def blog_add(request):
	if request.method == 'POST':
		form = BlogForm(request.POST)
		if form.is_valid():
			blog = form.save()
			return HttpResponseRedirect('/blog/list/')
	else:
		form = BlogForm()

	return render_to_response('snippet/blog.html', {'form': form},
			context_instance=RequestContext(request))

