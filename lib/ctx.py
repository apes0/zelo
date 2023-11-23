from typing import TYPE_CHECKING

import trio
from .api.window import Window

if TYPE_CHECKING:
    from .backends.generic import CData, GScreen, GWindow, GMouse, GCtx
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

    def getWindow(self, _id: int) -> 'GWindow':
        if _id == self._root:
            return self.root
        window = self.windows.get(_id)  # type: ignore
        if not window:
            window: GWindow = Window(0, 0, 0, _id, self)
            window.ignore = False  # probably true if we are missing it lol
            self.windows[_id] = window
        return window
