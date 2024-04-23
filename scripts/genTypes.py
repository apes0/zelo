import sys
import os
from itertools import chain
from typing import Callable
import re

path = os.path.join(os.path.dirname((os.path.realpath(__file__))), '..')

sys.path.append(path)
os.chdir(path)


def toCamelCase(name: str, cls: bool = False) -> str:
    parts = name.split('_')
    out = parts[0].capitalize() if cls else parts[0]

    for part in parts[1:]:
        out += part.capitalize()

    return out


def generate(_name, lib, ffi) -> str:
    # NOTE: this is a mess lol
    name = f'{_name}_cffi'
    defined = {}

    text = ''

    text += f'''from _cffi_backend import _CDataBase
from {name} import lib, ffi
from .base import Base, parseArgs

NULL = ffi.NULL

# types
'''
    for _type in set(chain.from_iterable(ffi.list_types())):
        try:
            obj = ffi.new(f'{_type}*')

            text += f'''
class {toCamelCase(_type, cls=True)}(Base):
    def __init__(self, obj):
        self.obj = obj
        if obj == ffi.NULL:
            return
'''
            for attr in dir(obj):
                tp = type(getattr(obj, attr))
                text += (
                    f'        self.{toCamelCase(attr)}: {tp.__name__} = obj.{attr}\n'
                )
            defined[_type] = toCamelCase(_type, cls=True)
        except:
            text += f'\n# skipping {toCamelCase(_type, cls=True)}, because its not fully defined\n'

    text += '''
# funcs

'''
    defs = open(f'lib/backends/ffi/{_name}/definitions.h').read()
    src = open(f'lib/backends/ffi/{_name}/source.c').read()

    for name, val in lib.__dict__.items():
        if isinstance(val, Callable):
            tp = re.findall(f'\n([^\n]*) +\\*?{name}\\(', defs)[0]
            _tp = defined.get(tp)
            text += f'{toCamelCase(name)} = lambda *a: {_tp if _tp else ""}(lib.{name}(*parseArgs(a)))\n'
        #            text += f'{toCamelCase(name)} = lambda *a: (print("called {toCamelCase(name)}") or {_tp if _tp else ""}(lib.{name}(*parseArgs(a))))\n' # debug lol
        else:
            text += f'{toCamelCase(name)}: {type(val).__name__} = lib.{name}\n'

    return text


from xcb_cffi import lib, ffi

open('./lib/backends/xcb.py', 'w').write(generate('xcb', lib, ffi))

from wayland_cffi import lib, ffi

open('./lib/backends/waylandServer.py', 'w').write(generate('wayland', lib, ffi))

from cairo_cffi import lib, ffi

open('./lib/backends/cairo.py', 'w').write(generate('cairo', lib, ffi))
