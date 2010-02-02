# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, \
         HttpResponseBadRequest
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from yadb.forms import BlogForm, UploadFileForm
from yadb import rst_tex, rst_code
from yadb.utils import slugify
from yadb.models import Blog
from yadb.decorators import superuser_only, ajax_required

import os


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
    """
    This show list of all posts pubblished but if you are authenticated
    let you see also the (yours) unpubblished.
    """
    real_Q = Q(status='pubblicato')

    if request.user.is_authenticated():
        real_Q = real_Q | ( Q(user=request.user) & Q(status='bozza') )

    blogs = Blog.objects.filter(real_Q).order_by('-creation_date')
    return render_to_response('yadb/blog_list.html',
            {'blogs': blogs},
            context_instance=RequestContext(request))

def blog_view(request, slug):
    """
    Read article by Tim Berners Lee about importance of URL
    """
    form = None
    content = None
    blog = get_object_or_404(Blog, slug=slug)

    return render_to_response('yadb/blog.html', {'blog': blog},
            context_instance=RequestContext(request))

@login_required
def blog_add(request, id=None):
    instance = None
    if id:
        instance = get_object_or_404(Blog, pk=id)

    form = BlogForm(request.POST or None, instance=instance)

    if request.method == 'POST':
        if form.is_valid():
            blog = form.save(commit=False)
            # TODO: maybe exists a Django function for slugify
            blog.slug = slugify(blog.title)
            blog.user = request.user
            blog.save()
            return HttpResponseRedirect('/blog/')

    return render_to_response('yadb/blog.html', {'form': form},
            context_instance=RequestContext(request))

def find_a_free_number(basename):
    # TODO: more pythonic
    idx = 0
    while 1:
        idx += 1
        filename = basename + '.' + str(idx)
        try:
            os.stat(filename)
        except OSError:
            return filename


@login_required
def upload(request):
    form = UploadFileForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            filez = request.FILES['file']

            # write all the file in memory in a file with the same name
            # TODO: read it in chunks and check for overwriting.
            filename = settings.UPLOAD_PATH + filez.name
            try:
                os.stat(filename)
                destination = open(find_a_free_number(filename),'wb')
            except OSError:
                destination = open(filename, 'wb')

            destination.write(filez.read())
            destination.close()

            return HttpResponseRedirect(reverse('blog-list'))

    return render_to_response('upload.html',
            {'form': form}, RequestContext(request))
