from types import ModuleType
from functools import partial
from typing import Callable
from cffi import FFI
import os
from importlib import import_module

# NOTE: personally, i would name it 'xcbcffi' (or 'xcbCffi'), but there is already a module with that name and i
# don't want to use camel case for modules..., so ye, its gonna be in snake case

xcb = 'xcb_cffi'
wayland = 'libwayland_cffi'
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
    build, 'xcb', ['xcb', 'xcb-util', 'xcb-image', 'xcb-keysyms', 'xcb-randr'], xcb
)
buildCairo = partial(
    build, 'cairo', ['pango', 'pangoft2', 'fontconfig', 'freetype2'], cairo
)


def buildWayland():
    pass


def assertModule(imp, build):
    try:
        _lib = import_module(imp)
    except:
        build()


runningX = (
    True  # TODO: actually check if x is running, this is for future wayland support
)

imp, _build = (xcb, buildX) if runningX else (wayland, buildWayland)
imp: str
_build: Callable

assertModule(imp, _build)  # assert that we have the xcb/wayland module
assertModule(cairo, buildCairo)  # assert that we have the cairo module


def load(
    mod: str,
) -> (
    ModuleType
):  # this imports from the wrapper for you, but it also resolves circular imports
    return import_module(wrappers[imp] + f'.{mod}')
