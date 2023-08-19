from lib.extension import Extension
from typing import TYPE_CHECKING
from .windowTracker import Tracker

if TYPE_CHECKING:
    from lib.ctx import Ctx
    from lib.window import Window


class Tiler(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        super().__init__(ctx, cfg)
        self.mainSize: int
        self.mainId = 0
        self.border: int
        self.spacing: int
        Tracker(self, self.update)

    def update(self, _windows):
        main = None
        windows = []
        for window in _windows:
            if window.mapped:
                if window.id == self.mainId:
                    main = window
                    continue
                windows.append(window)
        if not main and windows:
            main = windows.pop(0)
            self.mainId = main.id
        size = 1 / max(len(windows), 1)
        y = self.spacing
        _height = (self.ctx.screen.height_in_pixels) * size - (2 + size) * self.spacing
        height = round(_height)
        offset = _height - height
        width = round(
            self.ctx.screen.width_in_pixels * (1 - self.mainSize) - self.spacing * 3
        )
        for window in windows:
            window.configure(
                newX=round(
                    self.ctx.screen.width_in_pixels * self.mainSize + self.spacing
                ),
                newY=round(y),
                newHeight=height,
                newWidth=width,
                newBorderWidth=self.border,
            )
            y += height + self.spacing * 2 + offset
        if main:
            mainSize = self.mainSize if windows else 1
            main.configure(
                newX=self.spacing,
                newY=self.spacing,
                newWidth=round(
                    self.ctx.screen.width_in_pixels * mainSize - 3 * self.spacing
                ),
                newHeight=self.ctx.screen.height_in_pixels - 3 * self.spacing,
                newBorderWidth=self.border,
            )
