from lib.extension import Extension
from lib.backends.events import createNotify
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.ctx import Ctx
    from lib.backends.generic import GWindow


class Mouse(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.font: str = 'cursor'
        self.cursor: str = 'left_ptr'
        self.fore: int = 0
        self.back: int = 0xFFFFFF

        super().__init__(ctx, cfg)

        createNotify.addListener(self.set)

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
