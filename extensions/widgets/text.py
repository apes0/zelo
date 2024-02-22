from .widget import Widget
from lib.api.drawer import Text as _Text
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.ctx import Ctx


class Text(Widget):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.text: str
        self.font: str
        self.fore: int = ctx.cfg.theme.fore
        self.back: int = ctx.cfg.theme.back

        super().__init__(ctx, cfg, resolve={'fore': int, 'back': int})

        self._text = _Text(
            ctx,
            self.win,
            0,
            0,
            self.text,
            self.font,
            self.fore,
            self.back,
        )
        ctx.nurs.start_soon(self.setSize, self._text.width, self._text.height)

    async def draw(self):
        self._text.draw()
