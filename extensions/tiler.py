from lib.extension import Extension
from typing import TYPE_CHECKING
from lib.ffi import ffi, lib as xcb
from lib.types import mapRequestTC, unmapNotifyTC


if TYPE_CHECKING:
    from lib.ctx import Ctx
    from lib.window import Window


class Tiler(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        super().__init__(ctx, cfg)
        self.mainSize:int
        self.main:Window = None # type:ignore
        self.secondary:list[Window] = []
        self.border:int
        self.spacing:int

        self.addListener(xcb.XCB_MAP_REQUEST, self.mapWindow)
        self.addListener(xcb.XCB_UNMAP_NOTIFY, self.unmapWindow)

    def mapWindow(self, event):
        event = mapRequestTC(event)
        window = self.ctx.getWindow(event.window)
        if window not in self.secondary:
            if not self.main:
                self.main = window
            else:
                self.secondary.append(window)
            self.update()

    def update(self):
        size = 1 / max(len(self.secondary), 1)
        y = self.spacing
        height = round((self.ctx.screen.height_in_pixels) * size - self.spacing * 2)
        for window in self.secondary:
            window.configure(
                newX=round(self.ctx.screen.width_in_pixels * self.mainSize + self.spacing),
                newY=y,
                newHeight=height,
                newWidth=round(self.ctx.screen.width_in_pixels * (1-self.mainSize) - self.spacing * 2),
                newBorderWidth=self.border,
            )
            y += height + self.spacing * 2
        if self.main:
            mainSize = self.mainSize if self.secondary else 1
            self.main.configure(
                newX=self.spacing,
                newY=self.spacing,
                newWidth=round(self.ctx.screen.width_in_pixels * mainSize - 2*self.spacing),
                newHeight=self.ctx.screen.height_in_pixels - 2*self.spacing,
                newBorderWidth=self.border,
            )

    def unmapWindow(self, event):
        event = unmapNotifyTC(event)
        window = self.ctx.getWindow(event.window)
        if window in self.secondary:
            self.secondary.remove(window)
        elif window == self.main:
            if self.secondary:
                self.main = self.secondary.pop(0)
            else:
                self.main = None # type:ignore
        self.update()

