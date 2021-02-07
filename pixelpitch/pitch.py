'''
This script calculates pixel pitch in µm for cameras listed on geizhals.at.
'''

import urllib.request
import re
import html
from math import sqrt
from collections import namedtuple, defaultdict

# For fixed-lens cameras we assume 4:3 sensor aspect ratio if not given.
# Also, the following mapping of given sensor sizes to sensor areas is used from wikipedia:
# http://en.wikipedia.org/wiki/Image_sensor_format
# This seems necessary as the advertised sensor sizes are often larger than they actually are.
fixed_url = 'http://geizhals.eu/?cat=dcam&asuch=&bpmax=&v=e&plz=&dist=&mail=&fcols=1418&fcols=86&fcols=3377&bl1_id=1000&sort=artikel'

# For DSLR and EVIL cameras we use the specified sensor dimensions as is.
dslr_url = 'https://geizhals.eu/?cat=dcamsp&xf=1480_Spiegelreflex+(DSLR)&asuch=&bpmin=&bpmax=&v=e&hloc=at&hloc=de&hloc=pl&hloc=uk&hloc=eu&plz=&dist=&mail=&fcols=166&fcols=5761&fcols=3378&sort=artikel&bl1_id=1000'
evil_url = 'https://geizhals.eu/?cat=dcamsp&xf=1480_Spiegellos+(DSLM)&asuch=&bpmin=&bpmax=&v=e&hloc=at&hloc=de&hloc=pl&hloc=uk&hloc=eu&plz=&dist=&mail=&fcols=169&fcols=166&fcols=5761&fcols=3378&sort=artikel&bl1_id=1000'

size_re = re.compile(r'\(([\d\.]+)x([\d\.]+)mm')
type_re = re.compile(r'<div class="productlist__additionalfilter">\s+(1/[\d\.]+)&quot;\s+</div>')
mpix_re = re.compile(r'<div class="productlist__additionalfilter">\s+([\d\.]+) Megapixel\s+</div>')
pitch_re = re.compile(r'<div class="productlist__additionalfilter">\s+([\d\.]+)µm\s+</div>')
year_re = re.compile(r'<div class="productlist__additionalfilter">\s+([\d]{4})\s+</div>')
name_re = re.compile(r'data-name="(.+?)"')

def sensor_area(width, height):
    return width*height

def sensor_size(diag, aspect):
    '''
    :param number diag: in inches
    :param number aspect: e.g. 4/3, or 3/2
    '''
    diagmm = diag * 25.4
    h = sqrt(diagmm**2/(aspect**2 + 1))
    w = aspect*h
    return w,h

# from http://en.wikipedia.org/wiki/Image_sensor_format
type_size = {'1/3.2': (4.54, 3.42),
             '1/3': (4.80, 3.60),
             '1/2.7': (5.37, 4.04),
             '1/2.5': (5.76, 4.29),
             '1/2.3': (6.17, 4.55),
             '1/2': (6.40, 4.80),
             '1/1.8': (7.18, 5.32),
             '1/1.7': (7.60, 5.70),
             '1/1.6': (8.08, 6.01),
             '1/1.5': (8.80, 6.60), # 2/3
             '1/1.2': (10.67, 8.00),
             '1': (13.20, 8.80),
             }

def sensor_size_from_type(typ, use_table):
    '''
    
    :param typ: e.g. 1/1.5"
    '''
    if not typ:
        return None
    if use_table and typ in type_size:
        return type_size[typ]
    if typ.startswith('1/'):
        diag = 1/float(typ[2:])
        size = sensor_size(diag, 4/3)
        return size
    return None

def pixel_pitch(area, mpix):
    '''
    :param area: sensor area in mm
    :param mpix: megapixels, e.g. 16.1
    :return: pixel pitch in µm 
    '''
    return 1000*sqrt(area/(mpix*10**6))

def extract_entries(url):
    print("Fetching " + url)
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0'),
                         ('Cookie', 'blaettern=1000')]
    html = opener.open(url).read().decode('utf-8')
    print("Response length: {}".format(len(html)))
    entries = re.findall(r'class="row productlist__product.+?<div class="productlist__bestpriceoffer">', html, re.DOTALL)
    assert entries
    print("Found {} entries".format(len(entries)))
    assert len(entries) > 0
    return entries

Spec = namedtuple('Spec', 'name type size pitch mpix year')

def extract_specs(entries):
    specs = []
    for entry in entries:
        name_match = name_re.search(entry)
        type_match = type_re.search(entry)
        size_match = size_re.search(entry)    
        pitch_match = pitch_re.search(entry)
        mpix_match = mpix_re.search(entry)
        year_match = year_re.search(entry)
        
        name = html.unescape(name_match.group(1))
        name = " ".join(name.split()) # removes consecutive whitespaces
        
        if type_match is not None:
            typ = type_match.group(1)
        else:
            typ = None
        
        if size_match is not None:
            width, height = float(size_match.group(1)), float(size_match.group(2))
            size = (width, height)
        else:
            size = None
        
        if pitch_match is not None:
            pitch = float(pitch_match.group(1))
        else:
            pitch = None
        
        if mpix_match is not None:
            mpix = float(mpix_match.group(1))
        else:
            mpix = None
            
        if year_match is not None:
            year = int(year_match.group(1))
        else:
            year = None
        
        specs.append(Spec(name, typ, size, pitch, mpix, year))
    
    specs = deduplicate_specs(specs)
    
    return specs

extras = ['weiß', 'schwarz', 'rot', 'grau', 'pink', 'gold', 'silber', 'violett', 'grün', 'blau',
          'orange', 'braun', 'gelb', 'beige', 'bordeaux', 'bronze', 'rosa', 'graphit', 'titan',
          'camouflage', 'khaki', 'anthrazit',
          'mit Objektiv', 'Gehäuse']
extras_re = re.compile('|'.join(extras))

parens_re = re.compile(r'\(.+\)$')

def deduplicate_specs(specs):
    '''
    Unifies product names and tries to remove duplicates which only differ
    in color, lens, etc.
    '''
    groups = defaultdict(list) # cleaned product name -> specs
    rest = []
    
    # unify product names and group possible identical cameras
    for spec in specs:
        match = extras_re.search(spec.name)
        if match:
            unified_name = spec.name[:match.start()]
            groups[unified_name].append(spec)
        else:
            rest.append(spec)
            
    # check if grouped cameras have the same sensor specs
    for unified_name, grouped_specs in groups.items():
        ref = grouped_specs[0]
        if all(spec.type == ref.type and spec.size == ref.size and spec.pitch == ref.pitch and spec.mpix == ref.mpix 
               for spec in grouped_specs):
            years = [s.year for s in grouped_specs if s.year]
            year = min(years) if years else None
            rest.append(Spec(unified_name, ref.type, ref.size, ref.pitch, ref.mpix, year))
        else:
            rest.extend(grouped_specs)
    
    # remove product numbers etc. in parentheses which are at the end of the name
    # also, strip whitespaces at start or end
    def remove_parens(spec):
        name = spec.name.strip()
        match = parens_re.search(name)
        if match:
            name = name[:match.start()].strip()
        return Spec(name, spec.type, spec.size, spec.pitch, spec.mpix, spec.year)
        
    rest = list(map(remove_parens, rest))
    
    return rest

SpecDerived = namedtuple('SpecDerived', 'spec size area pitch')

def derive_spec(spec, use_size_table=False):
    if spec.size is None:
        size = sensor_size_from_type(spec.type, use_size_table)
    else:
        size = spec.size
        
    if size is not None and spec.mpix is not None:
        area = size[0] * size[1]
    else:
        area = None

    if spec.pitch:
        pitch = spec.pitch
    elif spec.mpix is not None and area is not None:
        pitch = pixel_pitch(area, spec.mpix)
    else:
        pitch = None
    
    return SpecDerived(spec, size, area, pitch)

def derive_specs(specs, use_size_table=False):
    return list(map(lambda spec: derive_spec(spec, use_size_table), specs))

def get_fixed():
    entries = extract_entries(fixed_url)
    return derive_specs(extract_specs(entries), use_size_table=True)

def get_dslrs():
    entries = extract_entries(dslr_url)
    return derive_specs(extract_specs(entries), use_size_table=False)

def get_evils():
    entries = extract_entries(evil_url)
    return derive_specs(extract_specs(entries), use_size_table=False)

def get_all():
    return get_fixed() + get_dslrs() + get_evils()

def sorted_by(specs, key='pitch', reverse=True):
    fns = {'pitch': lambda c: c.pitch if c.pitch else -1,
           'area': lambda c: c.area if c.area else -1,
           'mpix': lambda c: c.spec.mpix if c.spec.mpix else -1,
           'name': lambda c: c.spec.name,
           }
    return sorted(specs, key=fns[key], reverse=reverse)
