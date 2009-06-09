from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

from snippet.forms import EntryForm

from snippet import rst_tex, rst_code

def test(request):
    formula = None
    if request.method != 'POST':
        form = EntryForm()
    else:
        form = EntryForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
	    formula = instance.content
	    # d41d8cd98f00b204e9800998ecf8427e = la stringa vuota
	    print 'formula: ', formula

    return render_to_response('homepage.html',
            {'form': form, 'entry':formula},
            context_instance=RequestContext(request))


