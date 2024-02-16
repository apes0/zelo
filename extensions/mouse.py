from lib.extension import Extension
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.ctx import Ctx


class Mouse(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.font: str = 'cursor'
        self.cursor: str = 'left_ptr'
        self.fore: int = 0
        self.back: int = 0xFFFFFF

        super().__init__(ctx, cfg)

        ctx.mouse.setCursor(
            ctx.root,
            self.font,
            self.cursor,
        )
