from lib.extension import Extension
from lib.backends.ffi import load
from typing import TYPE_CHECKING
from extensions.shotcuts import Shortcuts

if TYPE_CHECKING:
    from lib.ctx import Ctx


class Workspaces(Extension):  # TODO: make me work with the window tracker's focus queue
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        super().__init__(ctx, cfg)

        # these take the same thing as a shortcut (because they are shortcuts)
        self.next: tuple
        self.prev: tuple
        self.spaces = {}
        self.current = 0
        self.windows = []

        shortcuts: Shortcuts = self.assure(Shortcuts)  # type:ignore
        shortcuts.conf(
            {
                'shortcuts': {
                    **shortcuts.__dict__.get('shortcuts', {}),
                    self.next: self.nextSpace,
                    self.prev: self.prevSpace,
                }
            }
        )
        shortcuts.register()

    def nextSpace(self, ctx):
        self.hide()
        self.current += 1
        self.show()

    def prevSpace(self, ctx):
        if not self.current:
            return
        self.hide()
        self.current -= 1
        self.show()

    def hide(self):
        windows = []
        for window in self.ctx.windows.values():
            if window.mapped:
                windows.append(window)
        self.spaces[self.current] = {window.id: window for window in windows}
        for window in windows:
            window.unmap()

    def show(self):
        self.ctx.windows = self.spaces.get(self.current, {})
        self.windows = self.ctx.windows.values()
        for window in self.ctx.windows.values():
            window.map()
