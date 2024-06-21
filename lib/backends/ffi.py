import os
import sys
from functools import partial
from importlib import import_module
from types import ModuleType
from typing import Callable

from cffi import FFI

# NOTE: personally, i would name it 'xcbcffi' (or 'xcbCffi'), but there is already a module with that name and i
# don't want to use camel case for modules..., so ye, its gonna be in snake case

xcb = 'xcb_cffi'
wayland = 'wayland_cffi'
cairo = 'cairo_cffi'

wrappers = {xcb: 'lib.backends.x11', wayland: 'lib.backends.wayland'}


def build(name, libraries, out):
    # TODO: how to compile this elsewhere
    ffibuilder = FFI()

    ffibuilder.set_source_pkgconfig(
        out,
        libraries,
        open(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 'ffi', name, 'source.c'
            )
        ).read(),
    )

    ffibuilder.cdef(
        open(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'ffi',
                name,
                'definitions.h',
            )
        ).read(),
    )

    ffibuilder.compile(verbose=True, target='*')


buildX = partial(
    build,
    'xcb',
    [
        'xcb',
        'xcb-util',
        'xcb-image',
        'xcb-keysyms',
        'xcb-randr',
        'xcb-xtest',
        'xcb-errors',
    ],
    xcb,
)
buildCairo = partial(
    build, 'cairo', ['pango', 'pangoft2', 'fontconfig', 'freetype2'], cairo
)


buildWayland = partial(build, 'wayland', ['wayland-server'], wayland)


def assertModule(imp, build):
    try:
        # TODO: can we do this better?
        _lib = import_module(imp)
    except ModuleNotFoundError:
        build()


# TODO: auto decide, without an arg?
# TODO: make checks for each backend when we have more than wayland and x11

runningX: bool = len(sys.argv) == 1 or sys.argv[1] != '--wayland'

imp, _build = (xcb, buildX) if runningX else (wayland, buildWayland)
imp: str
_build: Callable

assertModule(imp, _build)  # assert that we have the xcb/wayland module
assertModule(
    cairo, buildCairo
)  # assert that we have the cairo module for text rendering


def load(
    mod: str,
) -> (
    ModuleType
):  # this imports from the wrapper for you, but it also resolves circular imports
    return import_module(wrappers[imp] + f'.{mod}')
