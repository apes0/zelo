from typing import TYPE_CHECKING, Any

import trio

from .api.window import Window

if TYPE_CHECKING:
    from ._cfg import Cfg
    from .backends.events import Event
    from .backends.generic import CData, GCtx, GMouse, GScreen, GWindow
    from .extension import Extension


class Ctx:
    def __init__(self):
        self._root: int
        self.root: GWindow
        self.dname: CData
        self.screenp: CData
        self.connection: CData
        self.screen: GScreen
        self.values: CData
        self.gctx: GCtx
        self.windows: dict[int, GWindow] = {}
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

        event.addListener(finish)

        await ev.wait()

        event.removeListener(finish)

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
