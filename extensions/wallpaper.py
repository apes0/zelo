from lib.extension import Extension
from typing import TYPE_CHECKING
from lib.backends.ffi import load
from lib.backends.events import createNotify, mapRequest, unmapNotify, destroyNotify


if TYPE_CHECKING:
    from lib.ctx import Ctx
    from lib.backends.generic import GImage

Image: type = load('drawer').Image


class Wallpaper(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        super().__init__(ctx, cfg)
        self.wall: str

        img = Image(
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
