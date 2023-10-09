from lib.extension import Extension
from typing import TYPE_CHECKING
from lib.backends.events import createNotify, mapRequest, unmapNotify, destroyNotify
from lib.api.drawer import Image

if TYPE_CHECKING:
    from lib.ctx import Ctx
    from lib.backends.generic import GImage


class Wallpaper(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.wall: str
        super().__init__(ctx, cfg)

        img: GImage = Image(
            ctx,
            ctx.root,
            self.wall,
            ctx.screen.width,
            ctx.screen.height,
            0,
            0,
        )

        createNotify.addListener(lambda *a: img.draw())
        mapRequest.addListener(lambda *a: img.draw())
        unmapNotify.addListener(lambda *a: img.draw())
        destroyNotify.addListener(lambda *a: img.draw())
