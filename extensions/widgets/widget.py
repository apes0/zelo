# the base widget class

from typing import TYPE_CHECKING
from lib.extension import Extension

if TYPE_CHECKING:
    from lib.backends.generic import GWindow
    from lib.ctx import Ctx


class Widget(Extension):
    def __init__(self, ctx: 'Ctx', cfg: dict, resolve=[]) -> None:
        self.win: 'GWindow'
        self.x: int
        self.y: int

        super().__init__(ctx, cfg, resolve=resolve)

        self.x = int(self.x)
        self.y = int(self.y)
        self.size: tuple[int, int] = (1, 1)

        self.win = ctx.createWindow(
            self.x, self.y, 1, 1, 0, parent=self.win, ignore=True
        )
        # the window to draw in
        self.ctx.nurs.start_soon(self.win.map)
        self.win.redraw.addListener(self.draw)

    async def draw(self):
        raise NotImplementedError

    async def setSize(self, width: int, height: int):
        #        print(f'resizing to {width}x{height}')
        await self.win.configure(newWidth=width, newHeight=height)

        self.size = (width, height)
