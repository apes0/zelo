from lib.extension import Extension
from typing import TYPE_CHECKING
from lib.backends.events import buttonPress, mapRequest, focusChange
from lib.api.keys import Mod
from lib.api.mouse import Button

if TYPE_CHECKING:
    from lib.ctx import Ctx
    from lib.backends.generic import GButton, GWindow, GMod


class MouseFocus(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.buttons: list[GButton] = [
            Button('left'),
            Button('right'),
            Button('middle'),
        ]

        self.mod: GMod = Mod('any')

        super().__init__(ctx, cfg)

        buttonPress.addListener(self.buttonPress)
        mapRequest.addListener(self.mapWindow)
        focusChange.addListener(self.focusChange)

        for win in ctx.windows.values():
            for button in self.buttons:
                button.grab(self.ctx, win, self.mod)

    async def mapWindow(self, _win):
        for window in self.ctx.windows.values():
            for button in self.buttons:
                button.grab(self.ctx, window, self.mod)

    async def buttonPress(self, button: 'GButton', mod: 'GMod', window: 'GWindow'):
        for button in self.buttons:
            button.ungrab(self.ctx, window, self.mod)
        window.setFocus(True)

    async def focusChange(self, old: 'GWindow', new: 'GWindow'):
        for win in self.ctx.windows.values():
            for button in self.buttons:
                if win == new:
                    button.ungrab(self.ctx, win, self.mod)
                    continue
                button.grab(self.ctx, win, self.mod)
