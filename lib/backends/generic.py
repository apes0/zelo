import inspect
from typing import TYPE_CHECKING, Any
from collections.abc import Callable

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
        pres = []

        orobj = getattr(base, name)
        obj = getattr(cls, name)

        if hasattr(orobj, 'pres'):
            obj = getattr(cls, name)
            pres = orobj.pres

        if hasattr(obj, 'pres'):
            # pres from the child class take a lower priority
            pres += obj.pres

        if pres:
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
        self.ctx: Ctx = ctx
        self.focused = False
        self.mapped = False
        self.ignore: bool
        self.destroyed: bool
        self.parent: GWindow | None
        self.mine: bool

        # events:

        from .events import Event

        def trans(*a):
            return (*a, self)

        self.keyPress = Event[GKey, GMod](ctx, 'keyPress', {ctx.keyPress: trans})
        self.keyRelease = Event[GKey, GMod](ctx, 'keyRelease', {ctx.keyRelease: trans})
        self.buttonPress = Event[GButton, GMod](
            ctx, 'buttonPress', {ctx.buttonPress: trans}
        )
        self.buttonRelease = Event[GButton, GMod](
            ctx, 'buttonRelease', {ctx.buttonRelease: trans}
        )
        self.mapRequest = Event[()](ctx, 'mapRequest', {ctx.mapRequest: trans})
        self.mapNotify = Event[()](ctx, 'mapNotify', {ctx.mapNotify: trans})
        self.unmapNotify = Event[()](ctx, 'unmapNotify', {ctx.unmapNotify: trans})
        self.destroyNotify = Event[()](ctx, 'destroyNotify', {ctx.destroyNotify: trans})
        self.createNotify = Event[()](ctx, 'createNotify', {ctx.createNotify: trans})
        self.configureNotify = Event[()](
            ctx, 'configureNotify', {ctx.configureNotify: trans}
        )
        self.configureRequest = Event[()](
            ctx, 'configureRequest', {ctx.configureRequest: trans}
        )
        self.enterNotify = Event[()](ctx, 'enterNotify', {ctx.enterNotify: trans})
        self.leaveNotify = Event[()](ctx, 'leaveNotify', {ctx.leaveNotify: trans})
        self.redraw = Event[()](
            ctx, 'redraw', {ctx.redraw: trans}
        )  # exposure notify for x
        self.reparent = Event[GWindow](
            ctx, 'reparent', {ctx.reparent: trans}
        )  # my parent
        self.ignored = Event[()](
            ctx, 'ignored', {ctx.ignored: trans}
        )  # when we are marked as ignored

        # events that a backend makes:
        # TODO: this is a kinda shit solution
        # i think we can fix it by making proxy events or something like that

        self.titleChanged: Event
        self.iconTitleChanged: Event
        self.iconChanged: Event

    def __repr__(self) -> str:
        return f'<Window {self.id}>'

    async def names(self) -> list[str]:
        raise NotImplementedError

    async def title(self) -> str:
        raise NotImplementedError

    async def iconTitle(self) -> str:
        raise NotImplementedError

    async def icon(self) -> np.ndarray:
        raise NotImplementedError

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
    def __init__(self, ctx: 'Ctx[GCtx]') -> None:
        self.width: int
        self.height: int
        self.root: int
        self.screen: CData
        self.displays: list[GDisplay] = []
        raise NotImplementedError

    @logCall('screen', DEBUG)
    def turnOff(self):
        raise NotImplementedError

    @logCall('screen', DEBUG)
    def turnOn(self):
        raise NotImplementedError

    @logCall('screen', DEBUG)
    def setTimeout(self, t: int):
        raise NotImplementedError
        # ? should these be seperated

    @logCall('screen', DEBUG)
    def disableTimeout(self):
        raise NotImplementedError

    @logCall('screen', DEBUG)
    def enableTimeout(self):
        raise NotImplementedError

    def __repr__(self) -> str:
        return f'<Screen ({self.height} x {self.width})>'


# screen
class GDisplay:
    def __init__(self, ctx: 'Ctx', x: int, y: int, width: int, height: int) -> None:
        self.x: int
        self.y: int
        self.width: int
        self.height: int
        raise NotImplementedError

    @logCall('screen', DEBUG)
    async def scale(self, x: float, y: float):
        raise NotImplementedError

    def __repr__(self) -> str:
        return f'<Display {self.width}x{self.height}@({self.x}, {self.y})>'


# eventLoop
GEventLoop: Callable  # FIXME: this will not get caught when generating the api
