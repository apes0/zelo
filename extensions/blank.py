from typing import TYPE_CHECKING

from lib.extension import Extension

if TYPE_CHECKING:
    from lib.ctx import Ctx


class Blank(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.timeout: int = 10 * 60

        super().__init__(ctx, cfg)

        # TODO: when we can listen for timeout changes, re-set the timeout any time it changes
        if self.timeout >= 0:
            self.ctx.screen.enableTimeout()
            self.ctx.screen.setTimeout(self.timeout)
        else:
            self.ctx.screen.disableTimeout()
