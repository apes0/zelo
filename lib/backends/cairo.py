from _cffi_backend import _CDataBase
from cairo_cffi import lib, ffi
from .base import Base, parseArgs

NULL = ffi.NULL

# types

class FtBitmap(Base):
    def __init__(self, obj):
        self.obj = obj
        if obj == ffi.NULL:
            return
        self.buffer: _CDataBase = obj.buffer
        self.numGrays: int = obj.num_grays
        self.palette: _CDataBase = obj.palette
        self.paletteMode: int = obj.palette_mode
        self.pitch: int = obj.pitch
        self.pixelMode: int = obj.pixel_mode
        self.rows: int = obj.rows
        self.width: int = obj.width

# skipping FtBitmap, because its not fully defined

# funcs

render = lambda *a: FtBitmap(lib.render(*parseArgs(a)))
