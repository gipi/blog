# http://www.hvergi.net/2008/06/restructuredtext-extensions/comment-page-1/
import tempfile
import os
import sha
import shutil
 
def tex_wrap_formula(formula, font_size, latex_class):
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

def tikz_render_formula(formula, folder, font_size=11, latex_class='article'):
    hash = sha.new(formula).hexdigest()
    if os.path.exists(os.path.join(folder, hash + ".png")):
        return hash + ".png"
 
    tempdir = tempfile.mkdtemp()
    curpath = os.getcwd()
    os.chdir(tempdir)
 
    f = file('formula.tex', 'w')
    f.write(tikz_wrap_formula(formula))
    f.close()
 
    status = os.system("tex --interaction=nonstopmode formula.tex")
    assert 0==status, tempdir
 
    status = os.system("dvips -E formula.dvi -o formula.ps")
    assert 0==status, tempdir
 
    status = os.system("convert -density 120 -trim -transparent \"#FFFFFF\" formula.ps formula.png")
    assert 0==status, tempdir
 
    os.chdir(curpath)
 
    shutil.copyfile(os.path.join(tempdir, "formula.png"), os.path.join(folder, hash + ".png"))
    shutil.rmtree(tempdir)
 
    return hash+".png"

def tex_render_formula(formula, folder, font_size=11, latex_class='article'):
    hash = sha.new(formula).hexdigest()
    if os.path.exists(os.path.join(folder, hash + ".png")):
        return hash + ".png"
 
    tempdir = tempfile.mkdtemp()
    curpath = os.getcwd()
    os.chdir(tempdir)
 
    f = file('formula.tex', 'w')
    f.write(tex_wrap_formula(formula, font_size, latex_class))
    f.close()
 
    status = os.system("tex --interaction=nonstopmode formula.tex")
    assert 0==status, tempdir
 
    status = os.system("dvips -E formula.dvi -o formula.ps")
    assert 0==status, tempdir
 
    status = os.system("convert -density 120 -trim -transparent \"#FFFFFF\" formula.ps formula.png")
    assert 0==status, tempdir
 
    os.chdir(curpath)
 
    shutil.copyfile(os.path.join(tempdir, "formula.png"), os.path.join(folder, hash + ".png"))
    shutil.rmtree(tempdir)
 
    return hash+".png"


