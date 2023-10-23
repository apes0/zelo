from lib.extension import Extension, perDisplay
from typing import TYPE_CHECKING
from lib.backends.events import createNotify, mapRequest, unmapNotify, destroyNotify
from lib.api.drawer import Image

if TYPE_CHECKING:
    from lib.ctx import Ctx
    from lib.backends.generic import GImage, GDisplay


@perDisplay
class Wallpaper(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.wall: str
        self.display: GDisplay
        super().__init__(ctx, cfg)

        img: GImage = Image(
            ctx,
            ctx.root,
            self.wall,
            self.display.width,
            self.display.height,
            self.display.x,
            self.display.y,
        )

        createNotify.addListener(lambda *a: img.draw())
        mapRequest.addListener(lambda *a: img.draw())
        unmapNotify.addListener(lambda *a: img.draw())
        destroyNotify.addListener(lambda *a: img.draw())
