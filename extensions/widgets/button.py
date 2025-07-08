from typing import TYPE_CHECKING
from collections.abc import Callable

from lib.api.drawer import Rectangle
from lib.backends.generic import GRectangle
from lib.extension import initExt
from lib.api.mouse import Button as _Button

from .widget import Widget


if TYPE_CHECKING:
    from lib.ctx import Ctx


class Button(Widget):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.widget: type[Widget] | None = None
        self.cfg: dict = {}
        self.back: int = ctx.cfg.theme.back
        self.width = 50
        self.height = 50
        self.fn: Callable

        super().__init__(ctx, cfg, resolve={'back': int})

        self._widget: Widget
        self.bg: GRectangle

    async def __ainit__(self):
        await super().__ainit__()

        self.bg = Rectangle(
            self.ctx, self.win, 0, 0, self.width, self.height, self.back
        )
        if self.widget:
            self._widget = await initExt(
                self.widget, ctx, {**cfg, 'win': self.win, 'x': 0, 'y': 0}
            )
            self._widget.win.buttonPress.addListener(self.buttonPress)
        else:
            _Button('left').grab(self.ctx, self.win)
            self.win.buttonPress.addListener(self.buttonPress)

        await self.setSize(self.width, self.height)

    async def buttonPress(self, button, mod):
        self.fn(button, mod)

    async def setSize(self, width: int, height: int):
        self.bg.resize(width, height)
        return await super().setSize(width, height)

    async def draw(self):
        self.bg.draw()
        if self.widget:
            await self._widget.draw()
