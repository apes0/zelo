from lib.extension import Extension
from typing import TYPE_CHECKING
from .windowTracker import Tracker

if TYPE_CHECKING:
    from lib.ctx import Ctx

# tiles windows in the following way:
#
# Every window takes up ``1/len(windows)`` of the screen horizontally, and goes to the bottom of the
# screen vertically.
# __________________________
# |    |     |    |   |    |
# | #1 |  #2 | #3 |#4 | #5 |
# |____|_____|____|___|____|

# FIXME: wobbly


class Tiler(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        super().__init__(ctx, cfg)
        self.border: int
        self.spacing: int
        Tracker(self, self.update)

    def update(self, windows):
        size = 1 / max(len(windows), 1)
        x = self.spacing
        width = round((self.ctx.screen.width) * size - self.spacing * 2)
        for window in windows.values():
            window.configure(
                newX=x,
                newY=self.spacing,
                newHeight=self.ctx.screen.height - 2 * self.spacing,
                newWidth=width,
                newBorderWidth=self.border,
            )
            x += width + self.spacing * 2
