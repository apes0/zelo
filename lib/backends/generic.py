import cffi
import _cffi_backend
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..ctx import Ctx

# these are definitions for what functions and classes the backends should have

# TODO: make everything here raise NotImplementedError, so that if something is missing in the
# backend, we will be told

CData = _cffi_backend._CDataBase  # cffi.FFI.CData


class GConnection:
    def __init__(self) -> None:
        self.conn: cffi.FFI.CData

    def disconnect(self):
        pass


# TODO: use this in ctx, basically as a ctx for the backend
class GCtx:
    def __init__(self) -> None:
        pass


class GWindow:
    def __init__(
        self, height: int, width: int, borderWidth: int, _id: int, ctx: 'Ctx'
    ) -> None:
        self.id: int
        self.height: int
        self.width: int
        self.borderWidth: int
        self.x: int = 0
        self.y: int = 0
        self.ctx: 'Ctx' = ctx
        self.focused = False
        self.mapped = False
        self.age: int  # used for auto focus

    def map(self):
        pass

    def unmap(self):
        pass

    def setFocus(self, focus):
        pass

    def configure(
        self, newX=None, newY=None, newWidth=None, newHeight=None, newBorderWidth=None
    ):
        pass


class GMod:
    def __init__(self, *names: str) -> None:
        self.mod: int


class GKey:
    def __init__(self, lable: str) -> None:
        self.lable: str = lable
        self.key: int | None = None

    def load(self, ctx: 'Ctx'):
        pass

    def grab(self, ctx: 'Ctx', *modifiers: GMod):
        pass

    def ungrab(self, ctx: 'Ctx'):
        pass


class GButton:
    def __init__(self, lable: str | None = None, button: int | None = None) -> None:
        self.lable: str
        self.button: int

    def grab(self, ctx: 'Ctx', window: GWindow, *mods: GMod):
        pass

    def ungrab(self, ctx: 'Ctx', window: GWindow, *mods: GMod):
        pass


class GImage:
    def __init__(
        self,
        ctx: 'Ctx',
        window: GWindow,
        imgPath: str,
        width: int,
        height: int,
        x: int,
        y: int,
    ) -> None:
        pass

    def draw(self):
        pass


class GScreen:
    def __init__(self) -> None:
        self.width: int
        self.height: int
        self.root: int
        self.screen: CData
