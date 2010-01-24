from docutils import nodes, utils
from docutils.parsers.rst import directives, roles
from django.conf import settings
import texrender
 
def get_img(formula,render_func):
    print 'DEBUG of formula: ', formula
    return render_func(formula, settings.TEX_MEDIA)

def get_latex_img(formula):
    return get_img(formula, texrender.tex_render_formula)

def get_tikz_img(formula):
    return get_img(formula, texrender.tikz_render_formula)



def directive(get_img_func, name, arguments, options, content, lineno,
        content_offset, block_text, state, state_machine):
    imagename = get_img_func('\n'.join(content))
    if imagename == 'error.png':
        return [nodes.raw('', '<b>Errore</b>', format='html')]

    url = settings.TEX_MEDIA_URL + imagename
    return [nodes.raw('', '<img class="tikz" src="%s" alt="tex generated images"/>' % url, format='html')]

def latex_directive(name, arguments, options, content, lineno,
        content_offset, block_text, state, state_machine):
    return directive(get_latex_img, name, arguments, options, content,
            lineno, content_offset, block_text, state, state_machine)

def tikz_directive(name, arguments, options, content, lineno,
        content_offset, block_text, state, state_machine):
    return directive(get_tikz_img, name, arguments, options, content,
            lineno, content_offset, block_text, state, state_machine)


latex_directive.content = 1
directives.register_directive('latex', latex_directive)

tikz_directive.content = 1
directives.register_directive('tikz', tikz_directive)
