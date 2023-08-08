from .ffi import ffi
from .window import Window
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ewmh import AtomStore
    from .extension import Extension


class Ctx:
    def __init__(self):
        self._root: int
        self.root: Window
        self.dname: ffi.CData
        self.screenp: ffi.CData
        self.connection: ffi.CData
        self.screen: ffi.CData
        self.values: ffi.CData
        self.shortcuts: dict
        self.windows: dict[int, Window] = {}
        self.focused: Window = None  # type:ignore
        self.atomStore: 'AtomStore'
        self.keys = []  # list to hold pressed keys for shortcuts
        self.extensions: list[Extension] = []  # list of loaded extensions

    def getWindow(self, _id: int) -> Window:
        if _id == self._root:
            return self.root
        window = self.windows.get(_id, None)
        if not window:
            window = Window(0, 0, 0, _id, self)
            self.windows[_id] = window
        return window
