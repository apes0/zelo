import os
import sys
from functools import partial
from importlib import import_module
from logging import DEBUG
from types import ModuleType
from collections.abc import Callable

from cffi import FFI

from ..debcfg import log

# TODO: export this to a config thing, mostly for tests and stuff

# NOTE: personally, i would name it 'xcbcffi' (or 'xcbCffi'), but there is already a module with that name and i
# don't want to use camel case for modules..., so ye, its gonna be in snake case

prefix = 'lib.backends.build'

xcb = 'xcb_cffi'
wayland = 'wayland_cffi'
pango = 'pango_cffi'
standalone = '_standalone'  # this doesn't need to get built lol

wrappers = {
    xcb: 'lib.backends.x11',
    wayland: 'lib.backends.wayland',
    standalone: 'lib.backends.standalone',
}


buildloc = os.path.abspath(os.path.join(__file__, '..', 'build'))


def build(name, libraries, out):
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

    ffibuilder.compile(
        verbose=True, tmpdir=buildloc, target=os.path.join(buildloc, f'{out}.*')
    )


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
        'xcb-xinerama',
        'xcb-dpms',
    ],
    xcb,
)
buildpango = partial(
    build, 'pango', ['pango', 'pangoft2', 'fontconfig', 'freetype2'], pango
)


buildWayland = partial(build, 'wayland', ['wayland-server'], wayland)

builds = {wayland: buildWayland, pango: buildpango, xcb: buildX, standalone: lambda: 0}


def assertModule(imp, build):
    try:
        # TODO: can we do this better?
        _lib = import_module(f'{prefix}.{imp}')
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

if not imp:
    raise BaseException("didn't manage to find a backend")

_build: Callable = builds[imp]

log('backend', DEBUG, f'chose backend {imp}')

assertModule(imp, _build)  # assert that we have the xcb/wayland module
assertModule(
    pango, buildpango
)  # assert that we have the pango module for text rendering


def load(
    mod: str,
) -> (
    ModuleType
):  # this imports from the wrapper for you, but it also resolves circular imports
    assert imp, 'ffi.load(): imp cannot be None'
    return import_module(f'{wrappers[imp]}.{mod}')
