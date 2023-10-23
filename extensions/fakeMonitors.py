from lib.extension import Extension
from typing import TYPE_CHECKING
from lib.api.screen import Display

if TYPE_CHECKING:
    from lib.ctx import Ctx
    from lib.backends.generic import GDisplay

# fakes screens
# TODO: vertical splitting
# TODO: the config is kinda shit, also gonna need to fix it when i add monitor names
# ?: for now, what do we do when we have less monitors than the config says


class FakeDisplays(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.displays: list[list[int]]  # widths for every screen

        super().__init__(ctx, cfg)

        for n, cfg in enumerate(self.displays):
            if not cfg:
                continue
            x = 0
            dpy: GDisplay = ctx.screen.displays[n]
            ctx.screen.displays.pop(n)
            for width in cfg:
                new = Display(x, dpy.y, width, dpy.height)  # type: ignore
                x += width
                ctx.screen.displays.append(new)
