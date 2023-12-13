from lib.extension import Extension
from typing import TYPE_CHECKING
from extensions.shortcuts import Shortcuts

if TYPE_CHECKING:
    from lib.ctx import Ctx


class Workspaces(Extension):  # TODO: make me work with the window tracker's focus queue
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        # these take the same thing as a shortcut (because they are shortcuts)
        self.next: tuple
        self.prev: tuple
        self.move: tuple
        self.spaces = {}
        self.focuses = {}
        self.current = 0
        self.windows = []
        self.toMove = {}
        super().__init__(ctx, cfg)

        shortcuts: Shortcuts = Shortcuts(  # type:ignore
            ctx,
            {
                'shortcuts': {
                    self.next: self.nextSpace,
                    self.prev: self.prevSpace,
                    self.move: self.toggleMove,
                }
            },
        )
        shortcuts.register()

    def toggleMove(self, ctx: 'Ctx'):
        if not ctx.focused:
            return

        self.toMove[ctx.focused.id] = not self.toMove.get(ctx.focused.id, False)

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

        if self.ctx.focused and not self.toMove.get(self.ctx.focused.id):
            self.focuses[self.current] = self.ctx.focused

        for window in self.ctx.windows.values():
            if (
                window.mapped
                and not window.ignore
                and not self.toMove.get(window.id, False)
            ):
                windows.append(window)

        self.spaces[self.current] = {window.id: window for window in windows}

        for window in windows:
            window.unmap()

    def show(self):
        print(self.focuses)
        self.windows = list(self.spaces.get(self.current, {}).values())

        for window in self.windows:
            window.map()

        for win, move in self.toMove.items():
            if not move:
                continue
            self.windows.append(self.ctx.getWindow(win))

        self.toMove = {}

        if focused := self.focuses.get(self.current):
            focused.setFocus(True)

        self.ctx.windows = {win.id: win for win in self.windows}
