from typing import TYPE_CHECKING, Any

import trio

from lib.watcher import Watcher

from .api.window import Window

if TYPE_CHECKING:
    from ._cfg import Cfg
    from .backends.events import Event
    from .backends.generic import GCtx, GMouse, GScreen, GWindow
    from .extension import Extension


class Ctx:
    def __init__(self):
        self._root: int
        self.root: GWindow
        self.screen: GScreen
        self.gctx: GCtx
        self.windows: dict[int, GWindow] = {}
        self.watcher = Watcher(self)
        self.focused: GWindow | None = None
        self.mouse: GMouse
        self.extensions: dict[type, Extension] = {}  # list of loaded extensions
        self.closed = False
        self.nurs: trio.Nursery
        self.cfg: 'Cfg'

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

        event.addListener(self, finish)

        await ev.wait()

        event.removeListener(self, finish)

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

    def _getGCtx(self) -> Any:
        # NOTE: this was made for typing reasons
        # NOTE: basically, i just dont want to ``cast`` everywhere lol
        # NOTE: fuck python typing
        return self.gctx
