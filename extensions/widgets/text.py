from typing import TYPE_CHECKING

from lib.api.drawer import Text as _Text

from .widget import Widget

if TYPE_CHECKING:
    from lib.ctx import Ctx


class Text(Widget):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.text: str
        self.font: str
        self.fore: int = ctx.cfg.theme.fore
        self.back: int = ctx.cfg.theme.back

        super().__init__(ctx, cfg, resolve={'fore': int, 'back': int})

    async def __ainit__(self):
        await super().__ainit__()

        self._text = _Text(
            self.ctx,
            self.win,
            0,
            0,
            self.text,
            self.font,
            self.fore,
            self.back,
        )

        self.ready()
        await self.setSize(self._text.width, self._text.height)

    async def draw(self):
        self._text.draw()
