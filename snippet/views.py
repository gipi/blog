from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

from snippet.forms import EntryForm

# http://www.hvergi.net/2008/06/restructuredtext-extensions/comment-page-1/
import tempfile
import os
import hashlib
import shutil
 
def wrap_formula(formula, font_size, latex_class):
    return r"""\documentclass[%(font_size)spt]{%(latex_class)s}
               \usepackage[latin1]{inputenc}
               \usepackage{amsmath}
               \usepackage{amsfonts}
               \usepackage{amssymb}
               \pagestyle{empty}
               \newsavebox{\formulabox}
               \newlength{\formulawidth}
               \newlength{\formulaheight}
               \newlength{\formuladepth}
               \setlength{\topskip}{0pt}
               \setlength{\parindent}{0pt}
               \setlength{\abovedisplayskip}{0pt}
               \setlength{\belowdisplayskip}{0pt}
               \begin{lrbox}{\formulabox}
               $%(formula)s$
               \end{lrbox}
               \settowidth {\formulawidth}  {\usebox{\formulabox}}
               \settoheight{\formulaheight} {\usebox{\formulabox}}
               \settodepth {\formuladepth}  {\usebox{\formulabox}}
               \newwrite\foo
               \immediate\openout\foo=\jobname.depth
                   \addtolength{\formuladepth} {1pt}
                   \immediate\write\foo{\the\formuladepth}
               \closeout\foo
               \begin{document}
               \usebox{\formulabox}
               \end{document}""" % locals()

def render_formula(formula, folder, font_size=11, latex_class='article'):
    hash = hashlib.md5(formula).hexdigest()
    if os.path.exists(os.path.join(folder, hash + ".png")):
        return hash + ".png"
 
    tempdir = tempfile.mkdtemp()
    curpath = os.getcwd()
    os.chdir(tempdir)
 
    f = file('formula.tex', 'w')
    f.write(wrap_formula(formula, font_size, latex_class))
    f.close()
 
    status = os.system("latex --interaction=nonstopmode formula.tex")
    assert 0==status, tempdir
 
    status = os.system("dvips -E formula.dvi -o formula.ps")
    assert 0==status, tempdir
 
    status = os.system("convert -density 120 -trim -transparent \"#FFFFFF\" formula.ps formula.png")
    assert 0==status, tempdir
 
    os.chdir(curpath)
 
    shutil.copyfile(os.path.join(tempdir, "formula.png"), os.path.join(folder, hash + ".png"))
    shutil.rmtree(tempdir)
 
    return hash+".png"

def test(request):
    image_path = None
    if request.method != 'POST':
        form = EntryForm()
    else:
        form = EntryForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
	    formula = instance.content
	    print 'formula: ', formula
	    image_path = render_formula(formula, settings.TEX_MEDIA)

    return render_to_response('homepage.html',
            {'form': form, 'entry': "<img src=\"/media/TeX/%s\"/>" % image_path},
            context_instance=RequestContext(request))


