from lib.extension import Extension
from typing import TYPE_CHECKING
from lib.backends.events import mapNotify
import trio

if TYPE_CHECKING:
    from lib.ctx import Ctx
    from lib.backends.generic import GWindow


class Animation(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.frames: int = 5
        self.rate: float = 1 / 120
        self.fn = lambda x: x**2 * (3 - 2 * x)
        super().__init__(ctx, cfg)

        mapNotify.addListener(self.anim)

    async def anim(self, win: 'GWindow'):
        i = self.frames
        width = win.width
        height = win.height
        win.ignore = True
        time = trio.current_time()

        _rat = 0

        while i:
            _rat += 1 / self.frames
            rat = self.fn(_rat)

            await win.configure(
                newWidth=max(round(width * rat), 1),
                newHeight=max(round(height * rat), 1),
            )

            await trio.sleep_until(time := time + self.rate)
            i -= 1
        win.ignore = False
