from __future__ import division, print_function

def prettyprint(derived):
    spec = derived.spec
    
    print('"{}": '.format(spec.name), end='')
    
    if derived.size:
        print('{:.1f}x{:.1f}mm sensor'.format(*derived.size), end='')
        if spec.size is None:
            print(' (derived from type: {})'.format(spec.type), end='')
    else:
        print('unknown sensor size', end='')
    
    if spec.mpix:
        print(', {:.1f} MP'.format(spec.mpix), end='')
    else:
        print(', unknown resolution', end='')
        
    if derived.pitch:
        print(', {:.1f}µm pixel pitch'.format(derived.pitch), end='')
    
    print()