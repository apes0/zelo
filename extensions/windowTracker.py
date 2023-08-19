# A class for tilers to use, because its really annoying to keep track of windows
# NOTE: i literally made this just because of the workspaces hah

from lib.extension import Extension
from lib.types import mapRequestTC
from lib.ffi import ffi, lib as xcb
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from lib.ctx import Ctx
    from lib.window import Window


class Tracker:
    def __init__(self, tiler: Extension, updateFn: Callable):
        self.ctx: 'Ctx' = tiler.ctx
        self._update: Callable = updateFn
        self.windows = []

        tiler.addListener(xcb.XCB_MAP_REQUEST, self.mapWindow)
        tiler.addListener(xcb.XCB_UNMAP_NOTIFY, self.unmapWindow)
        tiler.addListener(xcb.XCB_DESTROY_NOTIFY, self.destroyNotify)

    def update(self):
        # sync with ctx, its important (workspaces changes the ctx.windows so ye)
        windows = []
        window: Window
        for window in self.ctx.windows.values():
            if not window.mapped:
                continue
            windows.append(window)
        print(windows)
        self._update(windows)

    def mapWindow(self, event):
        event = mapRequestTC(event)
        window: Window = self.ctx.getWindow(event.window)
        if window.x or window.y:
            return
        window.map()
        self.update()
        window.setFocus(True)

    def unmapWindow(self, _event):
        self.update()

    def destroyNotify(self, _event):
        self.update()
