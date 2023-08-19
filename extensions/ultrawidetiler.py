from lib.extension import Extension
from typing import TYPE_CHECKING
from lib.ffi import ffi, lib as xcb
from lib.types import mapRequestTC, unmapNotifyTC
from .windowTracker import Tracker

if TYPE_CHECKING:
    from lib.ctx import Ctx
    from lib.window import Window


class Tiler(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        super().__init__(ctx, cfg)
        self.border: int
        self.spacing: int
        Tracker(self, self.update)

    def update(self, windows):
        size = 1 / max(len(windows), 1)
        x = self.spacing
        width = round((self.ctx.screen.width_in_pixels) * size - self.spacing * 2)
        for window in windows:
            window.configure(
                newX=x,
                newY=self.spacing,
                newHeight=self.ctx.screen.height_in_pixels - 2 * self.spacing,
                newWidth=width,
                newBorderWidth=self.border,
            )
            x += width + self.spacing * 2
