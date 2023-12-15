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

        super().__init__(ctx, cfg)

        self.current = 0
        self.toMove = {}
        self.windows = {}
        self.focused = {}

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
        if self.ctx.focused and not self.toMove.get(self.ctx.focused.id):
            self.focused[self.current] = self.ctx.focused
            self.ctx.focused.setFocus(False)

        wins = []
        for win in self.ctx.windows.values():
            if not win.mapped or win.id in self.toMove.keys():
                continue

            win.unmap()
            wins.append(win)

        self.windows[self.current] = wins

    def show(self):
        for win in self.windows.get(self.current, []):
            win.map()

        focused = self.focused.get(self.current)
        if focused:
            focused.setFocus(True)

        self.toMove = {}
