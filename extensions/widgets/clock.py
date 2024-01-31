from .widget import Widget
from lib.api.drawer import Text
import time
import math
import trio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.ctx import Ctx


class Clock(Widget):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.fmt: str
        self.update = 1
        self.font: str
        self.fore: int = 0xFFFFFF
        self.back: int = 0x000000

        super().__init__(ctx, cfg, resolve=['fore', 'back'])

        self.text = Text(
            ctx,
            self.win,
            0,
            0,
            None,
            self.font,
            self.fore,
            self.back,
        )
        ctx.nurs.start_soon(self._update)

    async def _update(self):
        while True:
            ttime = math.floor(trio.current_time())
            text = time.strftime(self.fmt)
            self.text.set(text)
            await self.draw()
            await trio.sleep_until(ttime + self.update)

    async def draw(self):
        await self.setSize(self.text.width, self.text.height)
        self.text.draw()
