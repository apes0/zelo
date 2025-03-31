import inspect
from typing import TYPE_CHECKING, Any, Callable

import numpy as np

from ..debcfg import DEBUG, INFO, log, shouldLog

if TYPE_CHECKING:
    from ..ctx import Ctx

# these are definitions for what functions and classes the backends should have
# (basically a header file)
# NOTE: some methods are async when they dont use async functions - this is just for consistency

# CData = _cffi_backend._CDataBase  # cffi.FFI.CData
CData = Any

# NOTE: we need the file to load from in front of the class


# NOTE: this is the best logging solution i could come up with :3
# The other idea i had was to have every logged func be prefixed by a _ and then i could define the
# function without a _ here and use that to log, but i dont like that


def pre(fn):
    def deco(fn2):
        print('deco called')
        if hasattr(fn2, 'pres'):
            fn2.pres.insert(0, fn)
        else:
            fn2.pres = [fn]
        return fn2

    return deco


def logCall(name: str | list[str], level: int):
    def deco(fn):
        msg = f'calling {fn.__qualname__}({{args}})'
        if shouldLog(name):
            return pre(
                lambda *a, **kwa: log(
                    name,
                    level,
                    msg.format(
                        args=(
                            ', '.join(map(repr, a))
                            + (
                                ', '
                                + ', '.join(f'{n}={repr(v)}' for n, v in kwa.items())
                                if kwa
                                else ''
                            )
                        )
                    ),
                )
            )(fn)
        else:
            return fn

    # ig the pyramids were built just by calling ``black`` on the land

    return deco


def applyPre(cls: type) -> type:
    def makea(pres, obj):
        async def f(*a, **kwa):
            for pre in pres:
                pre(*a, **kwa)
            return await obj(*a, **kwa)

        return f

    def make(pres, obj):
        def f(*a, **kwa):
            for pre in pres:
                pre(*a, **kwa)
            return obj(*a, **kwa)

        return f

    base = cls
    if cls.__base__ and cls.__base__ != object:  # check if we arent the base class
        base = cls.__base__

    for name in dir(base):
        orobj = getattr(base, name)

        if hasattr(orobj, 'pres'):
            obj = getattr(cls, name)
            pres = orobj.pres

            if hasattr(obj, 'pres'):
                # additional pres from the child class take a lower priority
                pres += obj.pres
            isasync = inspect.iscoroutinefunction(obj)

            newF = makea(pres, obj) if isasync else make(pres, obj)
            setattr(cls, name, newF)

    return cls


# connection
class GConnection:
    def __init__(self) -> None:
        self.conn: Any

    def __repr__(self) -> str:
        return '<Connection>'

    @logCall('backend', INFO)
    def disconnect(self):
        raise NotImplementedError


# gctx
class GCtx:
    def __init__(self, ctx: 'Ctx') -> None:
        self.ctx = ctx
        raise NotImplementedError

    def __repr__(self) -> str:
        return '<GCtx>'

    @logCall(['backend', 'windows'], DEBUG)
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

    @logCall(['backend', 'windows'], INFO)
    def disconnect(self):
        raise NotImplementedError


# window
class GWindow:
    def __init__(
        self, height: int, width: int, borderWidth: int, _id: int, ctx: 'Ctx'
    ) -> None:
        self.id: int = _id
        self.height: int = height
        self.width: int = width
        self.borderWidth: int = borderWidth
        self.x: int = 0
        self.y: int = 0
        self.ctx: 'Ctx' = ctx
        self.focused = False
        self.mapped = False
        self.ignore: bool
        self.destroyed: bool
        self.parent: GWindow | None
        self.mine: bool
        self.title: str | None = ''

        # events:

        from .events import Event

        self.keyPress = Event('keyPress', GKey, GMod)
        self.keyRelease = Event('keyRelease', GKey, GMod)
        self.buttonPress = Event('buttonPress', GButton, GMod)
        self.buttonRelease = Event('buttonRelease', GButton, GMod)
        self.mapRequest = Event('mapRequest')
        self.mapNotify = Event('mapNotify')
        self.unmapNotify = Event('unmapNotify')
        self.destroyNotify = Event('destroyNotify')
        self.createNotify = Event('createNotify')
        self.configureNotify = Event('configureNotify')
        self.configureRequest = Event('configureRequest')
        self.enterNotify = Event('enterNotify')
        self.leaveNotify = Event('leaveNotify')
        self.redraw = Event('redraw')  # exposure notify for x
        self.reparented = Event('reparented', GWindow)  # my parent
        self.ignored = Event('ignored')  # when we are marked as ignored

        # events that a backend makes:
        # NOTE: we can still put a default event but we are gonna destroy it immediately, so its a
        # pointless thing to do

        self.titleChanged: Event

    def __repr__(self) -> str:
        return f'<Window {self.id}>'

    @logCall('windows', DEBUG)
    async def toTop(self):
        raise NotImplementedError

    @logCall('windows', DEBUG)
    async def toBottom(self):
        raise NotImplementedError

    @logCall('windows', DEBUG)
    async def screenshot(
        self,
        x: int = 0,
        y: int = 0,
        width: int | None = None,
        height: int | None = None,
    ) -> np.ndarray:
        raise NotImplementedError

    @logCall('windows', DEBUG)
    async def map(self):
        raise NotImplementedError

    @logCall('windows', DEBUG)
    async def unmap(self):
        raise NotImplementedError

    @logCall('windows', DEBUG)
    async def setFocus(self, focus: bool):
        raise NotImplementedError

    @logCall('windows', DEBUG)
    async def configure(
        self,
        newX=None,
        newY=None,
        newWidth=None,
        newHeight=None,
        newBorderWidth=None,
    ):
        raise NotImplementedError

    @logCall('windows', DEBUG)
    async def reparent(self, parent: 'GWindow', x: int, y: int):
        raise NotImplementedError

    @logCall('windows', DEBUG)
    async def close(self):
        raise NotImplementedError

    @logCall('windows', DEBUG)
    async def kill(self):
        raise NotImplementedError

    @logCall('windows', DEBUG)
    async def setBorderColor(self, color: int):
        raise NotImplementedError


# keys
class GMod:
    def __init__(self, *names: str) -> None:
        self.names = names
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

    @logCall(['keys', 'grab'], DEBUG)
    def grab(self, ctx: 'Ctx', window: GWindow, *modifiers: GMod):
        raise NotImplementedError

    @logCall(['keys', 'grab'], DEBUG)
    def ungrab(self, ctx: 'Ctx', window: GWindow, *modifiers: GMod):
        raise NotImplementedError

    @logCall(['keys', 'press'], DEBUG)
    def press(self, ctx: 'Ctx', window: 'GWindow', *modifiers: GMod):
        raise NotImplementedError

    @logCall(['keys', 'press'], DEBUG)
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

    @logCall(['buttons', 'grab'], DEBUG)
    def grab(self, ctx: 'Ctx', window: GWindow, *mods: GMod):
        raise NotImplementedError

    @logCall(['buttons', 'grab'], DEBUG)
    def ungrab(self, ctx: 'Ctx', window: GWindow, *mods: GMod):
        raise NotImplementedError

    @logCall(['buttons', 'press'], DEBUG)
    def press(self, ctx: 'Ctx', window: 'GWindow', x: int, y: int, *modifiers: GMod):
        raise NotImplementedError

    @logCall(['buttons', 'press'], DEBUG)
    def release(
        self, ctx: 'Ctx', window: 'GWindow', x: int, y: int, *modifiers: GMod
    ):  # ? do we need x and y here?
        raise NotImplementedError


# mouse
class GMouse:
    def __init__(self, ctx: 'Ctx') -> None:
        raise NotImplementedError

    def __repr__(self) -> str:
        return '<Mouse>'

    async def location(self) -> tuple[int, int]:
        raise NotImplementedError

    @logCall('backend', DEBUG)
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
        self.ctx: Ctx = ctx
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.windowId = window.id
        raise NotImplementedError

    def __repr__(self) -> str:
        return '<Image>'  # TODO: more proper reprs lol

    @logCall('drawable', DEBUG)
    def draw(self):
        raise NotImplementedError

    @logCall('drawable', DEBUG)
    def set(self, img: np.ndarray):
        raise NotImplementedError

    @logCall('drawable', DEBUG)
    def destroy(self):
        raise NotImplementedError

    @logCall('drawable', DEBUG)
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
        return '<Rectangle>'  # TODO: proper repr lol

    @logCall('drawable', DEBUG)
    def draw(self):
        raise NotImplementedError

    @logCall('drawable', DEBUG)
    def resize(self, width: int, height: int):
        raise NotImplementedError

    @logCall('drawable', DEBUG)
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

    @logCall('drawable', DEBUG)
    def draw(self):
        raise NotImplementedError

    @logCall('drawable', DEBUG)
    def set(self, text: str):
        raise NotImplementedError

    @logCall('drawable', DEBUG)
    def destroy(self):
        raise NotImplementedError

    @logCall('drawable', DEBUG)
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
