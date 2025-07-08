import traceback
from typing import TYPE_CHECKING, Any, TypeVar
from collections.abc import Awaitable, Callable

import trio

from lib.watcher import Watcher

from .api.window import Window
from .debcfg import ERROR, log
from .backends.events import Event

if TYPE_CHECKING:
    from ._cfg import Cfg
    from .backends.generic import GCtx, GMouse, GScreen, GWindow
    from .extension import Extension


async def _wrapper(afn):
    try:
        await afn
    except:
        log('startSoon', ERROR, f'{afn} encountered:\n {traceback.format_exc()}')


_GCtx = TypeVar('_GCtx', bound='GCtx')


# idk if mypy can actually typecheck this; i get a crash when running mypy lib/ctx.py
# see this: https://github.com/python/mypy/issues/18996
class Ctx[_GCtx]:
    def __init__(self):
        self._root: int
        self.root: GWindow
        self.screen: GScreen
        self.gctx: _GCtx
        self.windows: dict[int, GWindow] = {}
        self.watcher = Watcher(self)
        self.focused: GWindow | None = None
        self.mouse: GMouse
        self.extensions: dict[type, Extension] = {}  # list of loaded extensions
        self.closed = False
        self.nurs: trio.Nursery
        self.cfg: Cfg
        self.gctxConf = {}

        # events:
        self.keyPress = Event['GKey', 'GMod', 'GWindow'](self, 'keyPress')
        self.keyRelease = Event['GKey', 'GMod', 'GWindow'](self, 'keyRelease')
        # ? maybe include the x and y coordinates, but idk
        self.buttonPress = Event['GButton', 'GMod', 'GWindow'](self, 'buttonPress')
        self.buttonRelease = Event['GButton', 'GMod', 'GWindow'](self, 'buttonRelease')
        self.mapRequest = Event['GWindow'](self, 'mapRequest')
        self.mapNotify = Event['GWindow'](self, 'mapNotify')
        self.unmapNotify = Event['GWindow'](self, 'unmapNotify')
        self.destroyNotify = Event['GWindow'](self, 'destroyNotify')
        self.createNotify = Event['GWindow'](self, 'createNotify')
        self.configureNotify = Event['GWindow'](self, 'configureNotify')
        self.configureRequest = Event['GWindow'](self, 'configureRequest')
        self.enterNotify = Event['GWindow'](self, 'enterNotify')
        self.leaveNotify = Event['GWindow'](self, 'leaveNotify')
        self.focusChange = Event['GWindow | None', 'GWindow | None'](
            self, 'focusChange'
        )  # old, new
        self.redraw = Event['GWindow'](self, 'redraw')  # exposure notify for x
        self.reparent = Event['GWindow', 'GWindow'](
            self, 'reparent'
        )  # window and its parent
        self.ignored = Event['GWindow'](
            self, 'ignored'
        )  # when a window is marked as ignored

    def getWindow(self, _id: int) -> 'GWindow':
        if _id == self._root:
            return self.root
        window = self.windows.get(_id)  # type: ignore
        if not window:
            window: GWindow = Window(0, 0, 0, _id, self)
            window.ignore = False  # probably true if we are missing it lol
            self.windows[_id] = window
        return window

    async def waitFor(self, event: 'Event') -> list[Any]:
        # returns the arguments for the event that has been triggered
        ev = trio.Event()
        args = []

        async def finish(*_args):
            ev.set()
            args.extend(_args)

        n = event.addListener(finish)

        await ev.wait()

        event.removeListener(n)

        return args

    def createWindow(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        borderWidth: int,
        parent: 'GWindow | None' = None,
        ignore: bool = False,
    ) -> 'GWindow':
        if not parent:
            parent = self.root
        win = self.gctx.createWindow(x, y, width, height, borderWidth, parent, ignore)
        self.windows[win.id] = win
        return win

    def editable(self, win: 'GWindow') -> bool:
        # tells us if we can touch a window
        # NOTE: we can always do shit to windows, but this basically checks if we should
        if (
            win.ignore
            or not win.mapped
            or win.id == self._root
            or win.destroyed
            or win.id not in self.windows
        ):
            return False

        return True

    def disconnect(self):
        self.gctx.disconnect()

    def startSoon(self, fn: Callable[..., Awaitable], *args):
        self.nurs.start_soon(_wrapper, fn(*args))
