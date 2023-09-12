from types import ModuleType
from typing import Callable
from cffi import FFI
import os
from importlib import import_module

# NOTE: personally, i would name it 'xcbcffi', but there is already a module with that name and i
# don't want to use snake case for modules..., so ye, its gonna be in snake case
xcb = "xcb_cffi"
wayland = "libwayland_cffi"

wrappers = {xcb: 'lib.backends.x11', wayland: 'lib.backends.wayland'}


def buildX():
    ffibuilder = FFI()

    ffibuilder.set_source(
        xcb,
        open(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 'ffi', 'xcb', 'source.c'
            )
        ).read(),
        libraries=['xcb', 'xcb-util', 'xcb-image', 'xcb-keysyms'],
    )

    ffibuilder.cdef(
        open(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'ffi',
                'xcb',
                'definitions.h',
            )
        ).read(),
        override=True,
    )

    ffibuilder.compile(verbose=True)


def buildWayland():
    pass


runningX = (
    True  # TODO: actually check if x is running, this is for future wayland support
)

imp, build = (xcb, buildX) if runningX else (wayland, buildWayland)
imp: str
build: Callable

try:
    _lib = import_module(imp)
except:
    build()


def load(
    mod: str,
) -> (
    ModuleType
):  # this imports from the wrapper for you, but it also resolves circular imports
    return import_module(wrappers[imp] + f'.{mod}')
