from cffi import FFI
import os

lib = "xcb_cffi"

def build():
    ffibuilder = FFI()

    ffibuilder.set_source(
        lib,
        open(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffi', 'source.c')
        ).read(),
        libraries=['xcb', 'xcb-util'],
    )

    ffibuilder.cdef(
        open(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffi', 'definitions.h')
        ).read(),
        override=True,
    )

    ffibuilder.compile(verbose=True)


try:
    _lib = __import__(lib)
except:
    build()
    _lib = __import__(lib)

lib = _lib.lib
ffi = _lib.ffi
