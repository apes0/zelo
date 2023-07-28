from .ffi import ffi
from .window import Window
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ewmh import AtomStore


class Ctx:
    def __init__(self):
        # TODO: make a seperate ``managedWindows``, so that we don't use the regular ``windows``
        # TODO: list, which may have unmapped, and therefore unmanaged by us, windows.
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

    def getWindow(self, _id: int) -> Window:
        window = self.windows.get(_id, None)
        if not window:
            window = Window(0, 0, 0, _id, self)
            self.windows[_id] = window
        return window
