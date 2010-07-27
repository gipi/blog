# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, \
         HttpResponseBadRequest
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.views.generic.list_detail import object_list

from tagging.models import Tag, TaggedItem

from yadb.forms import BlogForm, UploadFileForm
from yadb import rst_tex, rst_code, rst_video
from yadb.utils import slugify
from yadb.models import Blog
from yadb.decorators import superuser_only, ajax_required

import os, datetime, operator


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
    query = Blog.objects.get_authenticated(user=request.user)
    extra_context = {
        'latest_posts': query[:5],
        'comments': Comment.objects.all().order_by('-submit_date')[:5],
        'categories': Tag.objects.usage_for_queryset(query, counts=True),
    }
    return object_list(request,
            queryset=Blog.objects.get_authenticated(user=request.user),
            template_object_name='blog',
            template_name='yadb/blog_list.html',
            extra_context=extra_context)

def blog_archives(request):
    return object_list(request,
            queryset=Blog.objects.get_authenticated(user=request.user),
            template_object_name='blog',
            extra_context={'title': 'Archives'},
            template_name='yadb/archives_list.html')

def blog_categories(request, tags):
    query = Blog.objects.get_authenticated(user=request.user)
    q = TaggedItem.objects.get_by_model(query, tags)
    return object_list(request, queryset=q,
            template_object_name='blog',
            extra_context={'title': 'Categories'},
            template_name='yadb/archives_list.html')


@login_required
def blog_add(request, id=None):
    instance = None
    if id:
        instance = get_object_or_404(Blog, pk=id)

    form = BlogForm(request.POST or None, instance=instance)

    if request.method == 'POST':
        old_status = getattr(instance, 'status', None)
        if form.is_valid():
            # form.save change instance so must save the status before
            blog = form.save(commit=False)
            # TODO: maybe exists a Django function for slugify
            initial_slug = slugify(blog.title)

            # check for slug existence
            trailing = ''
            idx = 0
            try:
                while Blog.objects.get(slug=initial_slug + trailing):
                    idx += 1
                    trailing = '-%d' % idx
            except Blog.DoesNotExist:
                pass

            blog.slug = initial_slug + trailing
            blog.user = request.user

            if ( old_status == 'bozza') and (blog.status == 'pubblicato'):
                blog.creation_date = datetime.datetime.now()

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
            {'form': form}, context_instance=RequestContext(request))

@login_required
def uploaded(request):
    FILES_ROOT = settings.UPLOAD_PATH
    files = os.listdir(FILES_ROOT)

    couples = []
    for file in files:
        couples.append((file, os.stat(FILES_ROOT + file).st_mtime))

    couples = sorted(couples, key=operator.itemgetter(1), reverse=True)
    ordered_filenames = map(operator.itemgetter(0), couples)
    paginator = Paginator(ordered_filenames, 10)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        filez = paginator.page(page)
    except (EmptyPage, InvalidPage):
        filez = paginator.page(paginator.num_pages)

    return render_to_response('yadb/uploaded.html', {
        'UPLOAD_URL': settings.UPLOAD_URL,
        'files': filez}, context_instance=RequestContext(request))
