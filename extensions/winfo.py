from typing import TYPE_CHECKING, Any

import trio

from lib.api.drawer import Text
from lib.backends.events import enterNotify, leaveNotify
from lib.extension import Extension
from utils.fns import getDisplay

if TYPE_CHECKING:
    from lib.backends.generic import GWindow
    from lib.ctx import Ctx


class Winfo(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.upd = 1 / 60
        self.win = ctx.createWindow(1, 1, 1, 1, 5, ignore=True)
        self.following = False
        self.font = 'Ubuntu 20'
        self.fore = 0xFFFFFF
        self.back = 0
        self.xoff = 10
        self.yoff = 10
        self.text = Text(ctx, self.win, 0, 0, None, self.font, self.fore, self.back)

        # TODO: make these args
        # TODO: put this in the docs

        super().__init__(ctx, cfg)

        self.addListener(enterNotify, self.enter)
        self.addListener(leaveNotify, self.enter)
        self.addListener(self.win.redraw, self.redraw)

    async def enter(self, win: 'GWindow'):
        self.text.set(
            f'''id: {win.id}
focused: {win.focused}
ignore: {win.ignore}
destroyed: {win.destroyed}
mapped: {win.mapped}
mine: {win.mine}
parent: {win.parent}
title: {win.title}
x: {win.x} y: {win.y} w: {win.width} h: {win.height}'''
        )
        self.text.draw()
        await self.win.configure(newWidth=self.text.width, newHeight=self.text.height)
        await self.win.map()
        await self.win.toTop()
        self.following = True
        await self.follow()

    async def redraw(self):
        self.text.draw()

    async def leave(self, _win: 'GWindow'):
        self.following = False
        await self.win.unmap()

    async def follow(self):
        while self.following:
            (x, y) = await self.ctx.mouse.location()
            d = getDisplay(self.ctx, x, y)
            if not d:
                continue

            if (diff := y + self.yoff + self.win.height - d.height) > 0:
                y -= diff + self.yoff

            if (diff := x + self.xoff + self.win.width - d.width) > 0:
                x -= diff + self.xoff

            await self.win.configure(newX=x + self.xoff, newY=y + self.yoff)
            await trio.sleep(self.upd)
