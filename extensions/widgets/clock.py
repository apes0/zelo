import math
import time
from typing import TYPE_CHECKING

import trio

from lib.api.drawer import Text
from lib.backends.generic import GText

from .widget import Widget

if TYPE_CHECKING:
    from lib.ctx import Ctx


class Clock(Widget):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.fmt: str
        self.update = 1
        self.font: str
        self.fore: int = ctx.cfg.theme  # type: ignore
        self.back: int = ctx.cfg.theme  # type: ignore
        self.text: GText | None = None

        super().__init__(ctx, cfg, resolve={'fore': int, 'back': int})

    async def __ainit__(self):
        await super().__ainit__()

        self.text = Text(
            self.ctx,
            self.win,
            0,
            0,
            None,
            self.font,
            self.fore,
            self.back,
        )

        self.ready()
        self.ctx.startSoon(self._update)

    async def _update(self):
        assert self.text, 'clock._update must to be started after __ainit__'

        while True:
            ttime = math.floor(trio.current_time())
            text = time.strftime(self.fmt)
            self.text.set(text)
            await self.draw()
            await trio.sleep_until(ttime + self.update)

    async def draw(self):
        if not self.text:
            return

        await self.setSize(self.text.width, self.text.height)
        self.text.draw()
