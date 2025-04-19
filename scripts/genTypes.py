import importlib
import os
import sys
from itertools import chain
from typing import Callable

# WARN: touching this is hell, this whole thing took me like a week to figure out
# This is what the output should resemble:
# class Ptr[T](Base):
#     def __init__(obj: T):
#         self.obj: T = obj
#
# type CPtr[T] = T
#
# # native type, ptr
# def asdf(a: Ptr[int], b: int) -> Ptr[int]:
#       return Ptr(somefunc(a.obj, a))
#
# # ctype, ptr
# def asdf(a: Ptr[int], b: int) -> CPtr[CType]:
#       return CType(somefunc(a.obj, a))
#
# # native type, not ptr
# def asdf(a: Ptr[int], b: int) -> int:
#       return int(somefunc(a.obj, a))
#
# # ctype, not ptr
# def asdf(a: Ptr[int], b: int) -> CType:
#       return CType(somefunc(a.obj, a))


path = os.path.join(os.path.dirname((os.path.realpath(__file__))), '..')

sys.path.append(path)
os.chdir(path)


def toCamelCase(name: str, cls: bool = False) -> str:
    parts = name.split('_')
    # TODO: change this to use .lower if its not a class
    out = parts[0].capitalize() if cls else parts[0]

    for part in parts[1:]:
        if not part:
            part = '_'
        out += part.capitalize()

    return out


def parseType(t):
    # TODO: what the fuck
    # (meaning rewrite this)
    # FIXME: this doesnt work with pointers to pointers
    # TODO: add variable names, instead of using a1, a2, etc..

    deflater = False
    parts = t.split(' ')
    i = 0

    custom = False

    if parts[i] == 'unsigned':
        i += 1

    if parts[i] == 'struct' or parts[i] == 'enum':
        i += 1
        deflater = True
        custom = True

    tname = parts[i]

    type = ''

    if not custom:
        type = {
            'int': 'int',
            'short': 'int',
            'float': 'int',
            'long': 'int',
            'char': 'int',
            'void': 'void',
            '_Bool': 'bool',
        }.get(tname, None)

        if type is None:
            custom = True
            type = toCamelCase(tname, cls=True)
    else:
        type = toCamelCase(tname, cls=True)

    i += 1

    ptr = ('C' if custom else '') + 'Ptr[{t}]'
    itype = type

    _ptr = len(parts) > i and parts[i] == '*'
    if _ptr:
        itype = ptr.format(t=type)

    cast = type
    if not custom and _ptr:
        cast = f'Ptr'

    itype = f"'{itype}'" if deflater else itype

    return itype, cast


def insert(fn, an):
    # NOTE: this is a debugging thingie
    #    return f'print(f"calling {fn}({",".join(f"{{a{n}}}" for n in range(an))})");'
    return ''


def generate(_name, lib, ffi) -> str:
    # NOTE: this is a mess lol
    name = f'{_name}_cffi'
    defined = {}

    defs = open(f'lib/backends/ffi/{_name}/definitions.h').read().splitlines()
    # src = open(f'lib/backends/ffi/{_name}/source.c').read()

    text = ''

    text += f'''from _cffi_backend import _CDataBase
from {name} import lib, ffi
from typing import Any, Literal
from .base import Base, parseArgs, Ptr, CPtr, void

NULL = ffi.NULL

# types
'''
    enums = ''
    for _type in sorted(set(chain.from_iterable(ffi.list_types()))):
        # check if _type is an enum
        enum = False
        for n, l in enumerate(defs):
            if '//' in l:
                l = l.split('//')[0].strip(' ')
            if l == f'typedef enum {_type}':
                enum = True
                eitems = []
                for l in defs[n + 2 :]:
                    if '}' in l:
                        break
                    eitems.append(f"'{toCamelCase(l.split('=')[0].strip())}'")
                enums += (
                    f'type {toCamelCase(_type, True)} = Literal['
                    + ', '.join(eitems)
                    + ']\n'
                )

        if enum:
            continue

        # else we will type it as a class
        try:
            obj = ffi.new(f'{_type}*')

            text += f'''class {toCamelCase(_type, cls=True)}(Base):
    def __init__(self, obj):
        self.obj = obj
        if obj == ffi.NULL:return
'''
            for attr in dir(obj):
                tp = type(getattr(obj, attr))
                text += (
                    f'        self.{toCamelCase(attr)}: {tp.__name__} = obj.{attr}\n'
                )
            defined[_type] = toCamelCase(_type, cls=True)
        except:
            text += f'''# skipping {toCamelCase(_type, cls=True)}, because its not fully defined
class {toCamelCase(_type, cls=True)}(Base):
    def __init__(self, obj):
        self.obj = obj
'''

    text += '''
# funcs and vars
'''

    for name, val in lib.__dict__.items():
        if isinstance(val, Callable):
            definition = val.__doc__.split('\n')[0]  # type: ignore
            parts = definition.split('(')[0].split(' ')
            fname = parts[-1]
            ptr = fname[0] == '*'
            rtype = ' '.join(parts[:-1])

            rtype, rcast = parseType(rtype + ' *' * ptr)
            args = definition.split('(')[1].strip(';').strip(')').split(',')
            types = ''
            callArgs = ''
            n = 0

            # find arg names

            argnames = []

            for l in defs:
                if '//' in l:
                    l = l.split('//')[0].strip(' ')
                if fname in l:
                    try:
                        _args = l.split('(')[1].strip(';').strip(')').split(',')
                        if len(_args) == len(args):
                            argnames = []
                            for arg in _args:
                                aname = arg.strip(' ').split(' ')[-1]
                                while aname.startswith('*'):
                                    aname = aname[1:]
                                argnames.append(aname.strip(' '))
                    except:
                        pass

            assert len(argnames) == len(
                args
            ), f'couldnt make definition for {fname}, fix your styling lol'

            for a, aname in zip(args, argnames):
                a = a.strip(' ')
                atype, _acast = parseType(a)
                types += f'{toCamelCase(aname)}: {atype}, '
                callArgs += f'{toCamelCase(aname)}, '
            text += f'\ndef {toCamelCase(name)}({types}) -> {rtype}:{insert(name, n)}return {rcast}(lib.{name}(*parseArgs({callArgs})))'
        else:
            text += (
                f'{toCamelCase(name)}: {type(val).__name__} = {lib.__dict__[name]}\n'
            )

    return text + '\n' + enums


def trybuild(libname, pyname):
    try:
        l = importlib.import_module(libname)
    except:
        print(f'couldn\'t generate {pyname}.py, compile {libname}')
        return
    open(f'./lib/backends/{pyname}.py', 'w').write(generate(pyname, l.lib, l.ffi))


trybuild('xcb_cffi', 'xcb')
trybuild('wayland_cffi', 'waylandServer')
trybuild('pango_cffi', 'pango')
