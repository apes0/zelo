from lib.extension import Extension
from typing import TYPE_CHECKING
from lib.ffi import ffi, lib as xcb
from lib.types import mapRequestTC, unmapNotifyTC

if TYPE_CHECKING:
    from lib.ctx import Ctx
    from lib.window import Window


class Tiler(Extension):
    def __init__(self) -> None:
        super().__init__('Tiler')
        self.windows = []
        self.border = 5
        self.spacing = 15

        self.addListener(xcb.XCB_MAP_REQUEST, self.mapWindow)
        self.addListener(xcb.XCB_UNMAP_NOTIFY, self.unmapWindow)


    def mapWindow(self, event):
        event = mapRequestTC(event)
        window = self.ctx.getWindow(event.window)
        if window not in self.windows:
            self.windows.append(window)
            self.update()

    def update(self):
        size = 1 / max(len(self.windows), 1)
        x = self.spacing
        width = round((self.ctx.screen.width_in_pixels) * size - self.spacing * 2)
        for window in self.windows:
            window.configure(
                newX=x,
                newY=self.spacing,
                newHeight=self.ctx.screen.height_in_pixels - 2 * self.spacing,
                newWidth=width,
                newBorderWidth=self.border,
            )
            x += width + self.spacing * 2

    def unmapWindow(self, event):
        event = unmapNotifyTC(event)
        window = self.ctx.getWindow(event.window)
        if window in self.windows:
            self.windows.remove(window)
            self.update()
