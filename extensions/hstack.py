from lib.extension import Extension
from typing import TYPE_CHECKING
from .windowTracker import track

if TYPE_CHECKING:
    from lib.ctx import Ctx
    from lib.backends.generic import GDisplay, GWindow

# tiles windows in the following way:
#
# Every window takes up ``1/len(windows)`` of the screen horizontally, and goes to the bottom of the
# screen vertically.
# __________________________
# |    |     |    |   |    |
# | #1 |  #2 | #3 |#4 | #5 |
# |____|_____|____|___|____|

# FIXME: wobbly


@track('update')
class Tiler(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.border: int
        self.spacing: int
        self.display: GDisplay
        super().__init__(
            ctx,
            cfg,
            resolve={
                'border': int,
                'spacing': int,
            },
        )

    async def update(self, windows: list['GWindow']):
        x = self.spacing
        width = round(
            (self.display.width - (2 + 2 * len(windows)) * self.spacing) / len(windows)
        )
        for window in windows:
            await window.configure(
                newX=x + self.display.x,
                newY=self.spacing + self.display.y,
                newHeight=self.ctx.screen.height - 3 * self.spacing,
                newWidth=width,
                newBorderWidth=self.border,
            )
            x += width + 2 * self.spacing
