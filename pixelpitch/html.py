from __future__ import absolute_import, print_function

from jinja2 import Environment, PackageLoader
import os
import sys
from datetime import datetime
import urllib.parse

from pixelpitch import pitch

env = Environment(loader=PackageLoader('pixelpitch', 'templates'))

def datetimeformat(value, format='%d %b %Y %H:%M:%S UTC'):
    return value.strftime(format)
env.filters['formatdate'] = datetimeformat

env.filters['urlencode'] = urllib.parse.quote_plus

def render():
    template = env.get_template('pixelpitch.html')
    specs_fixedlens = pitch.sorted_by(pitch.get_fixed(), 'pitch')
    html_fixedlens = template.render(title='Fixed-lens Cameras',
                                    specs=specs_fixedlens,
                                    page='fixedlens',
                                    date=datetime.utcnow())
    
    specs_dslr = pitch.sorted_by(pitch.get_dslrs(), 'pitch')
    html_dslr = template.render(title='DSLR Cameras',
                                specs=specs_dslr,
                                page='dslr',
                                date=datetime.utcnow())
    
    specs_evil = pitch.sorted_by(pitch.get_evils(), 'pitch')
    html_evil = template.render(title='EVIL Cameras',
                                specs=specs_evil,
                                page='evil',
                                date=datetime.utcnow())
    
    specs_all = pitch.sorted_by(specs_fixedlens + specs_evil + specs_dslr, 'pitch')
    html_all = template.render(title='All Cameras',
                               specs=specs_all,
                               page='all',
                               date=datetime.utcnow())
    
    template = env.get_template('about.html')
    html_about = template.render(page='about')
    
    return html_fixedlens, html_dslr, html_evil, html_all, html_about

def render_save(folder):
    assert os.path.isdir(folder)
    html_fixedlens, html_dslr, html_evil, html_all, html_about = render()
    
    _write(os.path.join(folder, 'fixedlens.html'), html_fixedlens)
    _write(os.path.join(folder, 'dslr.html'), html_dslr)
    _write(os.path.join(folder, 'evil.html'), html_evil)
    _write(os.path.join(folder, 'index.html'), html_all)
    _write(os.path.join(folder, 'about.html'), html_about)
    
def main():
    if len(sys.argv) == 2:
        folder = os.path.abspath(sys.argv[1])
    else:
        folder = os.path.abspath(os.path.curdir)
    render_save(folder)
    print('HTML files written to ' + folder)
    
def _write(path, content):
    with open(path, 'w', encoding='utf-8') as fp:
        fp.write(content)
