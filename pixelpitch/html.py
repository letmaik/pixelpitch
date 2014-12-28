from __future__ import absolute_import, print_function

from jinja2 import Environment, PackageLoader
from pixelpitch import pitch
import os
import sys

env = Environment(loader=PackageLoader('pixelpitch', 'templates'))

def render():
    template = env.get_template('pixelpitch.html')
    specs_compacts = pitch.sorted_by(pitch.get_compacts(), 'pitch')
    html_compacts = template.render(title='Compact Cameras',
                                    specs=specs_compacts,
                                    page='compact')
    
    specs_dslr = pitch.sorted_by(pitch.get_dslrs(), 'pitch')
    html_dslr = template.render(title='DSLR and System Cameras',
                                specs=specs_dslr,
                                page='dslr')
    
    specs_all = pitch.sorted_by(specs_compacts + specs_dslr, 'pitch')
    html_all = template.render(title='All Cameras',
                               specs=specs_all,
                               page='all')
    
    return html_compacts, html_dslr, html_all

def render_save(folder):
    assert os.path.isdir(folder)
    html_compacts, html_dslr, html_all = render()
    
    _write(os.path.join(folder, 'compact.html'), html_compacts)
    _write(os.path.join(folder, 'dslr.html'), html_dslr)
    _write(os.path.join(folder, 'index.html'), html_all)
    
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
