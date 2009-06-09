# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

from snippet.forms import EntryForm

from snippet import rst_tex, rst_code

example = """C e la costanza del suo valore
==============================

*Per adesso non usare le accentate che il server probably ha qualche problema con l'encoding straniero*

A sentence with links to Wikipedia_ and the `Linux kernel archive`_.

.. _Wikipedia: http://www.wikipedia.org/
.. _Linux kernel archive: http://www.kernel.org/


Si erano presentati vari problemi alla fine del secolo

* Equazioni di Maxwell non invarianti per trasformazioni di Galileo
* Catastrofe ultravioletta

Se voi aveste uno specchio in mano e decideste di andare alla velocit della luce, come si comporterebbe la vostra immagine?

.. latex:: \lim_{t\\to0}\\alpha + {1\over 1-\gamma^2}

Questo passava per la testa di Einstein nel 1905 e dintorni.

qui ci va il testo normale

.. code-block:: python 

 for item in list:
    print item

poi chi lo sa

.. code-block:: python
 :linenos:

 def pygments_directive(name, arguments, options, content, lineno,
                       content_offset, block_text, state, state_machine):
    try:
        lexer = get_lexer_by_name(arguments[0])
    except ValueError:
        print 'Warning: No lexer found!!!'
        # no lexer found - use the text one instead of an exception
        lexer = TextLexer()

    # take an arbitrary option if more than one is given
    formatter = options and VARIANTS[options.keys()[0]] or DEFAULT
    parsed = highlight(u'\\n'.join(content), lexer, formatter)
    parsed = '<div class="codeblock">%s</div>' % parsed
    return [nodes.raw('', parsed, format='html')]

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

    return render_to_response('homepage.html',
            {'form': form, 'entry':formula},
            context_instance=RequestContext(request))


