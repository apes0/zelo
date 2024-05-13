from typing import TYPE_CHECKING, Callable

import _cffi_backend
import cffi
import numpy as np

if TYPE_CHECKING:
    from ..ctx import Ctx
    from .events import Event

# these are definitions for what functions and classes the backends should have
# TODO: logging?
# NOTE: some methods are async when they dont use async functions - this is just for consistency

CData = _cffi_backend._CDataBase  # cffi.FFI.CData

# NOTE: we need the file to load from in front of the class


# connection
class GConnection:
    def __init__(self) -> None:
        self.conn: cffi.FFI.CData

    def __repr__(self) -> str:
        return '<Connection>'

    def disconnect(self):
        raise NotImplementedError


# TODO: use this in ctx, basically as a ctx for the backend
# gctx
class GCtx:
    def __init__(self, ctx: 'Ctx') -> None:
        self.ctx = ctx
        raise NotImplementedError

    def __repr__(self) -> str:
        return '<GCtx>'

    def sendEvent(self, event, window: 'GWindow') -> None:
        raise NotImplementedError

    def createWindow(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        borderWidth: int,
        parent: 'GWindow',
        ignore: bool,
    ) -> 'GWindow':
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
        self.destroyed: bool
        self.parent: GWindow | None
        self.mine: bool

        # events:

        self.keyPress: 'Event'
        self.keyRelease: 'Event'
        self.buttonPress: 'Event'
        self.buttonRelease: 'Event'
        self.mapRequest: 'Event'
        self.mapNotify: 'Event'
        self.unmapNotify: 'Event'
        self.destroyNotify: 'Event'
        self.createNotify: 'Event'
        self.configureNotify: 'Event'
        self.configureRequest: 'Event'
        self.enterNotify: 'Event'
        self.leaveNotify: 'Event'
        self.redraw: 'Event'

        raise NotImplementedError

    def __repr__(self) -> str:
        return f'<Window {self.id}>'

    async def toTop(self):
        raise NotImplementedError
        
    async def toBottom(self):
        raise NotImplementedError

    async def screenshot(self, x:int=0, y:int=0, width:int|None=None, height:int|None=None) -> np.ndarray:
        raise NotImplementedError

    async def map(self):
        raise NotImplementedError

    async def unmap(self):
        raise NotImplementedError

    async def setFocus(self, focus: bool):
        raise NotImplementedError

    async def configure(
        self,
        newX=None,
        newY=None,
        newWidth=None,
        newHeight=None,
        newBorderWidth=None,
    ):
        raise NotImplementedError

    async def close(self):
        raise NotImplementedError

    async def kill(self):
        raise NotImplementedError


# keys
class GMod:
    def __init__(self, *names: str) -> None:
        self.mod: int
        raise NotImplementedError

    def __repr__(self) -> str:
        return f'<Modifier {self.mod}>'


# keys
class GKey:
    def __init__(self, lable: str) -> None:
        self.lable: str = lable
        self.key: int | None = None
        raise NotImplementedError

    def __repr__(self) -> str:
        return f'<Key {self.lable} ({self.key})>'

    def load(self, ctx: 'Ctx'):
        raise NotImplementedError

    def grab(self, ctx: 'Ctx', window: GWindow, *modifiers: GMod):
        raise NotImplementedError

    def ungrab(self, ctx: 'Ctx', window: GWindow, *modifiers: GMod):
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

    def __repr__(self) -> str:
        return f'<Button {self.lable} ({self.button})>'

    def grab(self, ctx: 'Ctx', window: GWindow, *mods: GMod):
        raise NotImplementedError

    def ungrab(self, ctx: 'Ctx', window: GWindow, *mods: GMod):
        raise NotImplementedError

    def press(self, ctx: 'Ctx', window: 'GWindow', x: int, y: int, *modifiers: GMod):
        raise NotImplementedError

    def release(
        self, ctx: 'Ctx', window: 'GWindow', x: int, y: int, *modifiers: GMod
    ): #? do we need x and y here?
        raise NotImplementedError

# mouse
class GMouse:
    def __init__(self, ctx: 'Ctx') -> None:
        raise NotImplementedError

    def __repr__(self) -> str:
        return '<Mouse>'

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
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.windowId = window.id
        raise NotImplementedError

    def __repr__(self) -> str:
        return '<Image>'

    def draw(self):
        raise NotImplementedError

    def set(self, img: np.ndarray):
        raise NotImplementedError

    def destroy(self):
        raise NotImplementedError

    def move(self, x: int, y: int):
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

    def __repr__(self) -> str:
        return '<Rectangle>'

    def draw(self):
        raise NotImplementedError

    def resize(self, width: int, height: int):
        raise NotImplementedError

    def move(self, x: int, y: int):
        raise NotImplementedError


# drawer
class GText:
    def __init__(
        self,
        ctx: 'Ctx',
        win: 'GWindow',
        x: int,
        y: int,
        text: str | None,
        font: str,
        fore: int = 0xFFFFFF,
        back: int = 0x000000,
    ) -> None:
        self.x: int
        self.y: int
        self.text: str
        self.font: str
        self.image: GImage
        self.width: int
        self.height: int

    def __repr__(self) -> str:
        return f'<Text {self.text} with font {self.font}>'

    def draw(self):
        raise NotImplementedError

    def set(self, text: str):
        raise NotImplementedError

    def destroy(self):
        raise NotImplementedError

    def move(self, x: int, y: int):
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

    def __repr__(self) -> str:
        return '<Screen ({self.height} x {self.width})>'


# screen
class GDisplay:
    def __init__(self) -> None:
        self.x: int
        self.y: int
        self.width: int
        self.height: int
        raise NotImplementedError

    def __repr__(self) -> str:
        return '<Display ({self.x}, {self.y})>'


# eventLoop
GEventLoop: Callable  # FIXME: this will not get caught when generating the api
