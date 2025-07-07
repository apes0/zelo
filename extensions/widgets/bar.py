from typing import TYPE_CHECKING

from lib.api.drawer import Rectangle
from lib.extension import initExt

from .widget import Widget

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
        self.sizes = []

    async def initer(self, widget, cfg: dict):
        e = await initExt(widget, self.ctx, {**cfg, 'win': self.win, 'x': 0, 'y': 0})
        if e:
            self.insts.append(e)
        else:
            print('hhh')

    async def __ainit__(self):
        await super().__ainit__()
        for widget, cfg in self.widgets:
            await self.initer(widget, cfg)

        self.rect = Rectangle(
            self.ctx, self.win, 0, 0, self.width, self.height, self.back
        )

    async def draw(self):
        await self.setSize(self.width, self.height)
        self.rect.draw()
        for widget in self.insts:
            await widget.draw()

        await self.move()

    async def move(self):
        sizes = [widget._size for widget in self.insts]
        if sizes == self.sizes:
            return

        self.sizes = sizes

        s = sum([widget._size[0] for widget in self.insts])
        spacing = (self.width - s) / (max(len(self.insts), 1) + 1)
        assert spacing > 0, 'The bar is too small...'
        x = spacing

        for widget in self.insts:
            y = (self.height - widget._size[1]) // 2
            await widget.win.configure(newX=round(x), newY=y)
            x += spacing + widget._size[0]
