from _cffi_backend import _CDataBase
from pango_cffi import lib, ffi
from typing import Any
from .base import Base, parseArgs

# some random types to get shit to work

class Ptr[T](Base):
    def __init__(self, obj: T):
        self.obj: T = obj

type CPtr[T] = T

NULL = ffi.NULL
void = Ptr
enum = Ptr

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