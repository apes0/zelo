import os
import sys
from functools import partial
from importlib import import_module
from types import ModuleType
from typing import Callable
from logging import DEBUG

from ..debcfg import log

from cffi import FFI

# TODO: export this to a config thing, mostly for tests and stuff

# NOTE: personally, i would name it 'xcbcffi' (or 'xcbCffi'), but there is already a module with that name and i
# don't want to use camel case for modules..., so ye, its gonna be in snake case

xcb = 'xcb_cffi'
wayland = 'wayland_cffi'
cairo = 'cairo_cffi'
standalone = '_standalone'  # this doesn't need to get built lol

wrappers = {
    xcb: 'lib.backends.x11',
    wayland: 'lib.backends.wayland',
    standalone: 'lib.backends.standalone',
}


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

builds = {wayland: buildWayland, cairo: buildCairo, xcb: buildX, standalone: lambda: 0}


def assertModule(imp, build):
    try:
        # TODO: can we do this better?
        _lib = import_module(imp)
    except ModuleNotFoundError:
        build()


# TODO: auto decide, without an arg?
# TODO: make checks for each backend when we have more than wayland and x11

checks = {
    wayland: lambda: '--wayland' in sys.argv,
    standalone: lambda: '--standalone' in sys.argv,
    xcb: lambda: True,  # fallback lol
}
# TODO: check if there is $DISPLAY in env for xcb

imp: str | None = None
for lib, check in checks.items():
    if check():
        imp = lib
        break

assert imp, 'didn\'t manage to find a backend'

_build: Callable = builds[imp]

log('backend', DEBUG, f'chose backend {imp}')

assertModule(imp, _build)  # assert that we have the xcb/wayland module
assertModule(
    cairo, buildCairo
)  # assert that we have the cairo module for text rendering


def load(
    mod: str,
) -> (
    ModuleType
):  # this imports from the wrapper for you, but it also resolves circular imports
    return import_module(f'{wrappers[imp]}.{mod}')
