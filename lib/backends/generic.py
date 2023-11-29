import cffi
import _cffi_backend
from typing import TYPE_CHECKING, Callable
import numpy as np

if TYPE_CHECKING:
    from ..ctx import Ctx

# these are definitions for what functions and classes the backends should have

CData = _cffi_backend._CDataBase  # cffi.FFI.CData

# NOTE: we need the file to load from in front of the class


# connection
class GConnection:
    def __init__(self) -> None:
        self.conn: cffi.FFI.CData

    def disconnect(self):
        raise NotImplementedError


# TODO: use this in ctx, basically as a ctx for the backend
# gctx
class GCtx:
    def __init__(self, ctx: 'Ctx') -> None:
        self.ctx = ctx
        raise NotImplementedError

    def sendEvent(self, event, window: 'GWindow') -> None:
        raise NotImplementedError


# window
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
        self.ignore: bool
        self.parent: GWindow | None
        raise NotImplementedError

    def map(self):
        raise NotImplementedError

    def unmap(self):
        raise NotImplementedError

    def setFocus(self, focus):
        raise NotImplementedError

    def configure(
        self, newX=None, newY=None, newWidth=None, newHeight=None, newBorderWidth=None
    ):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError


# keys
class GMod:
    def __init__(self, *names: str) -> None:
        self.mod: int
        raise NotImplementedError


# keys
class GKey:
    def __init__(self, lable: str) -> None:
        self.lable: str = lable
        self.key: int | None = None
        raise NotImplementedError

    def load(self, ctx: 'Ctx'):
        raise NotImplementedError

    def grab(self, ctx: 'Ctx', *modifiers: GMod):
        raise NotImplementedError

    def ungrab(self, ctx: 'Ctx'):
        raise NotImplementedError

    def press(self, ctx: 'Ctx', window: 'GWindow', *modifiers: GMod):
        raise NotImplementedError

    def release(self, ctx: 'Ctx', window: 'GWindow', *modifiers: GMod):
        raise NotImplementedError


# mouse
class GButton:
    def __init__(self, lable: str | None = None, button: int | None = None) -> None:
        self.lable: str
        self.button: int
        raise NotImplementedError

    def grab(self, ctx: 'Ctx', window: GWindow, *mods: GMod):
        raise NotImplementedError

    def ungrab(self, ctx: 'Ctx', window: GWindow, *mods: GMod):
        raise NotImplementedError


# mouse
class GMouse:
    def __init__(self, ctx: 'Ctx') -> None:
        pass
        raise NotImplementedError

    def location(self) -> tuple[int, int]:
        raise NotImplementedError

    def setCursor(self, window: 'GWindow', _font: str, name: str, fore=None, back=None):
        raise NotImplementedError

    # TODO: maybe add grab and ungrab from button?


# drawer
class GImage:
    def __init__(
        self,
        ctx: 'Ctx',
        window: GWindow,
        img: np.ndarray | None,
        width: int,
        height: int,
        x: int,
        y: int,
    ) -> None:
        raise NotImplementedError

    def draw(self):
        raise NotImplementedError

    def set(self, img):
        raise NotImplementedError


# drawer
class GRectangle:  # ? maybe implement this for any polygon and then just use that for a rectangle
    def __init__(
        self,
        ctx: 'Ctx',
        window: 'GWindow',
        x: int,
        y: int,
        width: int,
        height: int,
        color: int = 0x000000FF,
    ) -> None:
        self.x: int
        self.y: int
        self.width: int
        self.height: int
        self.window: GWindow
        self.ctx: Ctx
        self.rect: CData
        raise NotImplementedError

    def draw(self):
        raise NotImplementedError


# screen
class GScreen:
    def __init__(self) -> None:
        self.width: int
        self.height: int
        self.root: int
        self.screen: CData
        self.displays: list[GDisplay] = []
        raise NotImplementedError


# screen
class GDisplay:
    def __init__(self) -> None:
        self.x: int
        self.y: int
        self.width: int
        self.height: int
        raise NotImplementedError


# eventLoop
GEventLoop: Callable  # FIXME: this will not get caught when generating the api
