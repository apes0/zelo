from lib.extension import Extension
from typing import TYPE_CHECKING
from extensions.shortcuts import Shortcuts, arun
from lib.utils import multiple

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
                    self.next: arun(ctx, self.nextSpace),
                    self.prev: arun(ctx, self.prevSpace),
                    self.move: arun(ctx, self.toggleMove),
                }
            },
        )
        shortcuts.register()

    def toggleMove(self, ctx: 'Ctx'):
        if not ctx.focused:
            return

        self.toMove[ctx.focused.id] = not self.toMove.get(ctx.focused.id, False)

    async def nextSpace(self, ctx):
        await self.hide()
        self.current += 1
        await self.show()

    async def prevSpace(self, ctx):
        if not self.current:
            return
        await self.hide()
        self.current -= 1
        await self.show()

    async def hide(self):
        if self.ctx.focused and not self.toMove.get(self.ctx.focused.id):
            self.focused[self.current] = self.ctx.focused

        wins = []

        for win in self.ctx.windows.values():
            if not win.mapped or win.ignore or win.id in self.toMove.keys():
                continue

            await win.unmap()
            wins.append(win)

        self.windows[self.current] = wins

    async def show(self):
        await multiple(*[win.map() for win in self.windows.get(self.current, [])])

        focused = self.focused.get(self.current)
        if focused:
            await focused.setFocus(True)

        self.toMove = {}
