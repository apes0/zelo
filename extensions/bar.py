from lib.extension import Extension
from typing import TYPE_CHECKING
from lib.backends.events import createNotify, mapRequest, unmapNotify, destroyNotify
from lib.api.drawer import Rectangle

if TYPE_CHECKING:
    from lib.ctx import Ctx
    from lib.backends.generic import GRectangle


class Bar(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.x: int
        self.y: int
        self.width: int
        self.height: int
        self.color: int = 0x000000
        super().__init__(ctx, cfg)

        rect: GRectangle = Rectangle(
            ctx, self.ctx.root, self.x, self.y, self.width, self.height
        )

        createNotify.addListener(lambda *a: rect.draw())
        mapRequest.addListener(lambda *a: rect.draw())
        unmapNotify.addListener(lambda *a: rect.draw())
        destroyNotify.addListener(lambda *a: rect.draw())
