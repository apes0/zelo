from lib.extension import Extension
from typing import TYPE_CHECKING
from lib.backends.events import buttonPress, mapRequest, enterNotify, leaveNotify
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

        enterNotify.addListener(self.enterNotify)
        leaveNotify.addListener(self.leaveNotify)
        buttonPress.addListener(self.buttonPress)
        mapRequest.addListener(self.mapWindow)

    def mapWindow(self, _win):
        for window in self.ctx.windows.values():
            self.button.grab(self.ctx, window, self.mod)

    def buttonPress(self, button: 'GButton', mod: 'GMod', window: 'GWindow'):
        self.button.ungrab(self.ctx, window, self.mod)
        window.setFocus(True)

    def enterNotify(self, win: 'GWindow'):
        # assure that we are waiting for a button press when hovering over a window

        if win == self.ctx.focused:
            return

        self.button.grab(self.ctx, win, self.mod)

    def leaveNotify(self, win: 'GWindow'):
        # ungrab the button when we stop hovering over the window
        self.button.ungrab(self.ctx, win, self.mod)
