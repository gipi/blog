# http://www.hvergi.net/2008/06/restructuredtext-extensions/comment-page-1/
import tempfile
import os
import sha
import shutil
 
def tex_wrap_formula(formula):
    return r"""
    \footline={}
    $$%(formula)s$$
    \end""" % locals()

def tikz_wrap_formula(formula):
    return r"""
    \input tikz
    \footline={}
    \tikzpicture %(formula)s \endtikzpicture
    \end""" % locals()

def tikz_render_formula(formula, folder):
	return render_formula(formula, tikz_wrap_formula, folder)

def tex_render_formula(formula, folder):
	return render_formula(formula, tex_wrap_formula, folder)

def render_formula(formula, fnc, folder, font_size=11, latex_class='article'):
    hash = sha.new(formula).hexdigest()
    if os.path.exists(os.path.join(folder, hash + ".png")):
        return hash + ".png"
 
    tempdir = tempfile.mkdtemp()
    curpath = os.getcwd()
    os.chdir(tempdir)
 
    f = file('formula.tex', 'w')
    f.write(fnc(formula))
    f.close()
 
    if os.system("tex --interaction=nonstopmode formula.tex") != 0:
	    os.chdir(curpath)
	    return 'error.png'
 
    if os.system("dvips -E formula.dvi -o formula.ps") != 0:
	    os.chdir(curpath)
	    return 'error.png'
 
    if os.system("convert -density 120 -trim -transparent \"#FFFFFF\" formula.ps formula.png") != 0:
	    os.chdir(curpath)
	    return 'error.png'
 
    os.chdir(curpath)
 
    shutil.copyfile(os.path.join(tempdir, "formula.png"), os.path.join(folder, hash + ".png"))
    shutil.rmtree(tempdir)
 
    return hash + ".png"
