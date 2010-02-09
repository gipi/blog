"""
This docutils' directive allow to include in your HTML document
a HTML5 video tag.

Example

.. video:: http://www.example.com/video/awesome_video.ogv

TODO: add option like :width:, :align: etc
"""
from docutils import nodes
from docutils.parsers.rst import directives

def video_directive(name, arguments, options, content, lineno,
        content_offset, block_text, state, state_machine):
    # TODO: take only the first line
    style = ""
    print options
    print arguments
    print content

    fmt_tag = '<div>%s</div>'

    # TODO: more useful align option
    if 'align' in options:
        fmt_tag = '<div align="center">%s</div>'

    tag = '<video width="400" src="%s" controls="" /></video>' % arguments[0]
    return [nodes.raw('', fmt_tag % tag, format='html')]

def align(argument):
    """Conversion function for the "align" option."""
    return directives.choice(argument, ('left', 'center', 'right'))


video_directive.content = 1
video_directive.arguments = (1, 0, 0)
video_directive.options = {
    'align': align,
}
directives.register_directive('video', video_directive)
