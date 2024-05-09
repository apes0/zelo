from lib.extension import Extension
from typing import TYPE_CHECKING
from lib.backends.events import buttonPress, mapNotify, focusChange
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

        for win in ctx.windows.values():
            if win.ignore:
                continue

            for button in self.buttons:
                button.grab(ctx, win, self.mod)

        self.addListener(buttonPress, self.buttonPress)
        self.addListener(mapNotify, self.mapNotify)
        self.addListener(focusChange, self.focusChange)

    async def mapNotify(self, win: 'GWindow'):
        if win.ignore or win.focused:
            return

        for button in self.buttons:
            print('i came', win.id)
            button.grab(self.ctx, win, self.mod)

    async def buttonPress(self, _button: 'GButton', mod: 'GMod', window: 'GWindow'):
        print(window, 'he came!')
        await window.setFocus(True)

    async def focusChange(self, old: 'GWindow | None', new: 'GWindow| None'):
        for button in self.buttons:
            if old:
                button.grab(self.ctx, old, self.mod)
            if new and new.focused:
                button.ungrab(self.ctx, new, self.mod)
