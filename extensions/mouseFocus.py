from lib.extension import Extension
from typing import TYPE_CHECKING
from lib.backends.events import buttonPress, mapRequest, focusChange
from lib.api.keys import Mod
from lib.api.mouse import Button

if TYPE_CHECKING:
    from lib.ctx import Ctx
    from lib.backends.generic import GButton, GWindow, GMod

# i found what enter notify and leave notify do here: (on line 853)
# https://gitlab.gnome.org/GNOME/mutter/-/blob/main/src/x11/events.c


class MouseFocus(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        super().__init__(ctx, cfg)

        # TODO: maybe export these to the config
        self.button: GButton = Button('any')
        self.mod: GMod = Mod('any')

        buttonPress.addListener(self.buttonPress)
        mapRequest.addListener(self.mapWindow)
        focusChange.addListener(self.focusChange)

        for win in ctx.windows.values():
            self.button.grab(self.ctx, win, self.mod)

    def mapWindow(self, _win):
        for window in self.ctx.windows.values():
            self.button.grab(self.ctx, window, self.mod)

    def buttonPress(self, button: 'GButton', mod: 'GMod', window: 'GWindow'):
        self.button.ungrab(self.ctx, window, self.mod)
        window.setFocus(True)

    def focusChange(self, old: 'GWindow', new: 'GWindow'):
        for win in self.ctx.windows.values():
            if win == new:
                self.button.ungrab(self.ctx, win, self.mod)
                continue
            self.button.grab(self.ctx, win, self.mod)
