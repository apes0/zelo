from typing import TYPE_CHECKING

from lib.api.keys import Key, Mod
from lib.extension import Extension
from utils.layout import Layout

from .shortcuts import Shortcuts, arun

if TYPE_CHECKING:
    from lib.backends.generic import GWindow
    from lib.ctx import Ctx


# combine multiple windows into one with tabs:
# _______________________________
# |   win   |   win   |   win   |
# |____1____|____2____|____3____|
# |                             |
# |         contents of         |
# |           current           |
# |             win             |
# |_____________________________|


# TODO: handle tabbed wins resizing
class Tab:
    def __init__(self, ctx: 'Ctx', win: 'GWindow') -> None:
        self.ctx = ctx
        self.win = win
        self.win.configureNotify.addListener(self.configureNotify)

        self.wins: list['GWindow'] = []
        self.cur: 'GWindow | None' = None

        layout = Layout()
        self.top, self.bottom = layout.hsplit(0.1, 0)

    async def configureNotify(self):
        await self.conf()

    async def conf(self):
        if not self.cur:
            return

        await self.cur.configure(
            newY=round(self.bottom.y.getRatio(self.win)),
            newHeight=round(self.bottom.height.getRatio(self.win)),
            newBorderWidth=0,
        )

    async def addWin(self, win: 'GWindow'):
        win.ignore = True
        self.cur = win
        await win.reparent(self.win, 0, 0)
        await self.conf()


class Tabs(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.create: tuple = ((Key('c'),), Mod('alt'))
        self.add: tuple
        self.remove: tuple
        self.next: tuple
        self.prev: tuple

        self.tabs: list[Tab] = []
        self.win: 'GWindow | None' = None

        super().__init__(ctx, cfg)

        shortcuts = Shortcuts(  # type:ignore
            ctx, {'shortcuts': {self.create: arun(ctx, self.createTab)}}
        )

        shortcuts.register()

        self.addListener(ctx.enterNotify, self.enterNotify)
        self.addListener(ctx.leaveNotify, self.leaveNotify)

    async def createTab(self, ctx: 'Ctx'):
        if not self.win:
            return

        win = ctx.createWindow(0, 0, 100, 100, 0)
        await win.map()

        tab = Tab(ctx, win)
        self.tabs.append(tab)
        await tab.addWin(self.win)

    async def enterNotify(self, win: 'GWindow'):
        self.win = win

    async def leaveNotify(self, win: 'GWindow'):
        self.win = None
