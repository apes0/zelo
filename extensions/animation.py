from typing import TYPE_CHECKING

import trio

from lib.backends.events import mapNotify
from lib.extension import Extension

if TYPE_CHECKING:
    from lib.backends.generic import GWindow
    from lib.ctx import Ctx


class Animation(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.frames: int = 10
        self.rate: float = 1 / 480
        self.fn = lambda x: x**2 * (3 - 2 * x)
        super().__init__(ctx, cfg)

        self.addListener(mapNotify, self.anim)

    async def anim(self, win: 'GWindow'):
        i = self.frames
        width = win.width
        height = win.height
        time = trio.current_time()

        _rat = 0

        def filter(w, *_):
            return w == win

        mapNotify.addFilter(self.ctx, filter)

        while i:
            win.ignore = True
            _rat += 1 / self.frames
            rat = self.fn(_rat)

            await win.configure(
                newWidth=max(round(width * rat), 1),
                newHeight=max(round(height * rat), 1),
            )

            await trio.sleep_until(time := time + self.rate)
            i -= 1
        win.ignore = False

        mapNotify.addFilter(self.ctx, filter)
