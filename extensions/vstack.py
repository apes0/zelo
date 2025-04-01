from typing import TYPE_CHECKING

from lib.extension import Extension

from .windowTracker import track

if TYPE_CHECKING:
    from lib.backends.generic import GDisplay, GWindow
    from lib.ctx import Ctx

# tiles windows in the following way:
#
# Every window takes up ``1/len(windows)`` of the screen vertically, and goes to the edges of the
# screen horizontally.
# |----------------------|
# |         #1           |
# |----------------------|
# |         #2           |
# |----------------------|
# |         #3           |
# |----------------------|
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
        y = self.spacing
        height = round(
            (self.display.height - (1 + 2 * len(windows)) * self.spacing) / len(windows)
        )
        for window in windows:
            await window.configure(
                newX=self.spacing + self.display.x,
                newY=y + self.display.y,
                newWidth=self.ctx.screen.width - 3 * self.spacing,
                newHeight=height,
                newBorderWidth=self.border,
            )
            y += height + 2 * self.spacing
