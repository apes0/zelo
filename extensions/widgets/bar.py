from .widget import Widget
from lib.api.drawer import Rectangle
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.ctx import Ctx


class Bar(Widget):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.back: int = ctx.cfg.theme.back
        self.height: int
        self.width: int
        self.widgets: list[tuple[type[Widget], dict]]

        super().__init__(
            ctx,
            cfg,
            resolve={'back': int, 'height': int, 'width': int, 'x': int, 'y': int},
        )

        self.insts: list[Widget] = []

        for widget, cfg in self.widgets:
            self.insts.append(widget(ctx, {**cfg, 'win': self.win, 'x': 0, 'y': 0}))

        self.rect = Rectangle(ctx, self.win, 0, 0, self.width, self.height, self.back)

        ctx.nurs.start_soon(self.draw)
        self.addListener(self.win.redraw, self.draw)

    async def draw(self):
        await self.setSize(self.width, self.height)
        self.rect.draw()
        for widget in self.insts:
            await widget.draw()

        await self.move()

    async def move(self):
        s = sum([widget._size[0] for widget in self.insts])
        spacing = (self.width - s) / (max(len(self.insts), 1) + 1)
        assert spacing > 0, 'The bar is too small...'
        x = spacing

        for widget in self.insts:
            y = (self.height - widget._size[1]) // 2
            await widget.win.configure(newX=round(x), newY=y)
            x += spacing + widget._size[0]
