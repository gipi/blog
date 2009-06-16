from docutils import nodes, utils
from docutils.parsers.rst import directives, roles
from django.conf import settings
import texrender
 
def get_latex_img(formula):
	print 'DEBUG of formula: ', formula
	fname = texrender.render_formula(formula, settings.TEX_MEDIA)
	return settings.TEX_MEDIA_URL + fname

def latex_directive(name, arguments, options, content, lineno,
		content_offset, block_text, state, state_machine):
	url = get_latex_img('\n'.join(content))
	return [nodes.raw('', '<img class="formula" src="%s" />' % url, format='html')]

latex_directive.content = 1
directives.register_directive('latex', latex_directive)
 
def get_tikz_img(formula):
	print 'DEBUG of formula: ', formula
	fname = texrender.tikz_render_formula(formula, settings.TEX_MEDIA)
	return settings.TEX_MEDIA_URL + fname

def tikz_directive(name, arguments, options, content, lineno,
		content_offset, block_text, state, state_machine):
	url = get_tikz_img('\n'.join(content))
	return [nodes.raw('', '<img class="tikz" src="%s" />' % url, format='html')]

tikz_directive.content = 1
directives.register_directive('tikz', tikz_directive)
