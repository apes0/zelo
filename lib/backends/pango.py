from typing import Any

from _cffi_backend import _CDataBase

from pango_cffi import ffi, lib

from .base import Base, CPtr, Ptr, enum, parseArgs, void

NULL = ffi.NULL

# types
class FtBitmap(Base):
    def __init__(self, obj):
        self.obj = obj
        if obj == ffi.NULL:return
        self.buffer: _CDataBase = obj.buffer
        self.numGrays: int = obj.num_grays
        self.palette: _CDataBase = obj.palette
        self.paletteMode: int = obj.palette_mode
        self.pitch: int = obj.pitch
        self.pixelMode: int = obj.pixel_mode
        self.rows: int = obj.rows
        self.width: int = obj.width

# funcs and vars

def render(text: Ptr[int], font: Ptr[int], back: int, fore: int, ) -> FtBitmap:return FtBitmap(lib.render(*parseArgs(text, font, back, fore, )))