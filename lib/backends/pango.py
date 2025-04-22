from _cffi_backend import _CDataBase
from pango_cffi import lib, ffi
from typing import Any, Literal
from .base import Base, parseArgs, Ptr, CPtr, void

NULL = ffi.NULL

# types
class FtBitmap(Base):
    def __init__(self, obj):
        self.obj = obj
        if obj == ffi.NULL:return
        self.buffer: Ptr[int] = obj.buffer
        self.numGrays: int = obj.num_grays
        self.palette: int = obj.palette
        self.paletteMode: int = obj.palette_mode
        self.pitch: int = obj.pitch
        self.pixelMode: int = obj.pixel_mode
        self.rows: int = obj.rows
        self.width: int = obj.width

# funcs and vars

def render(text: Ptr[int], font: Ptr[int], back: int, fore: int, ) -> FtBitmap:return FtBitmap(lib.render(*parseArgs(text, font, back, fore, )))
