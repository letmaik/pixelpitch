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
    specs_compacts = pitch.sorted_by(pitch.get_compacts(), 'pitch')
    html_compacts = template.render(title='Compact Cameras',
                                    specs=specs_compacts,
                                    page='compact',
                                    date=datetime.utcnow())
    
    specs_dslr = pitch.sorted_by(pitch.get_dslrs(), 'pitch')
    html_dslr = template.render(title='DSLR and System Cameras',
                                specs=specs_dslr,
                                page='dslr',
                                date=datetime.utcnow())
    
    specs_all = pitch.sorted_by(specs_compacts + specs_dslr, 'pitch')
    html_all = template.render(title='All Cameras',
                               specs=specs_all,
                               page='all',
                               date=datetime.utcnow())
    
    template = env.get_template('about.html')
    html_about = template.render(page='about')
    
    return html_compacts, html_dslr, html_all, html_about

def render_save(folder):
    assert os.path.isdir(folder)
    html_compacts, html_dslr, html_all, html_about = render()
    
    _write(os.path.join(folder, 'compact.html'), html_compacts)
    _write(os.path.join(folder, 'dslr.html'), html_dslr)
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
