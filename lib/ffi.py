from cffi import FFI
import os

ffibuilder = FFI()

lib = "xcb_cffi"

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


try:
    _lib = __import__(lib)
except:
    ffibuilder.compile(verbose=True)
    _lib = __import__(lib)

lib = _lib.lib
ffi = _lib.ffi
