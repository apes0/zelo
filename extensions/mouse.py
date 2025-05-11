from typing import TYPE_CHECKING

from lib.extension import Extension

if TYPE_CHECKING:
    from lib.backends.generic import GWindow
    from lib.ctx import Ctx


class Mouse(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.font: str = 'cursor'
        self.cursor: str = 'left_ptr'
        self.fore: int = 0
        self.back: int = 0xFFFFFF

        super().__init__(ctx, cfg)

        self.addListener(ctx.createNotify, self.set)

        ctx.mouse.setCursor(
            ctx.root,
            self.font,
            self.cursor,
        )

    async def set(self, win: 'GWindow'):
        self.ctx.mouse.setCursor(
            win,
            self.font,
            self.cursor,
        )
