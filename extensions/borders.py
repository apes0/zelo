from typing import TYPE_CHECKING

from lib.backends.events import createNotify, focusChange
from lib.extension import Extension

if TYPE_CHECKING:
    from lib.backends.generic import GWindow
    from lib.ctx import Ctx

# adds window borders


class Borders(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.width: int
        self.focused: int
        self.unfocused: int

        super().__init__(ctx, cfg)  # TODO: resolve stuff here

        self.addListener(createNotify, self.createNotify)
        self.addListener(focusChange, self.focusChange)

    async def createNotify(self, win: 'GWindow'):
        await win.configure(newBorderWidth=self.width)
        await win.setBorderColor(self.unfocused)

    async def focusChange(self, old: 'GWindow | None', new: 'GWindow | None'):
        if old:
            await old.setBorderColor(self.unfocused)
        if new:
            await new.setBorderColor(self.focused)
