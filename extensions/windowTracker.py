# A class for tilers to use, because its really annoying to keep track of windows
# NOTE: i literally made this just because of the workspaces hah

from logging import DEBUG
from lib.debcfg import log
from utils.fns import getDisplay
from lib.extension import Extension
from lib.backends.events import (
    mapRequest,
    destroyNotify,
    focusChange,
    unmapNotify,
    mapNotify,
    configureNotify,
)

from typing import TYPE_CHECKING, Callable, Coroutine

if TYPE_CHECKING:
    from lib.ctx import Ctx
    from lib.backends.generic import GWindow, GDisplay
    from lib.backends.events import Event


def track(updateFn: str, custom: list = []):
    def deco(ext: type[Extension]):
        class New(Extension):
            def __init__(self, ctx: 'Ctx', args: dict) -> None:
                super().__init__(ctx, {})
                Tracker(ext, ctx, updateFn, args, custom, self)

        return New

    return deco


def perDisplay(ctx: 'Ctx', wins: list['GWindow']):
    out: dict['GDisplay', list['GWindow']] = {}
    for win in wins:
        dpy = getDisplay(ctx, win.x, win.y)

        if not dpy:
            continue

        out[dpy] = [*out.get(dpy, []), win]

    return out


def removeAll(l: list['GWindow'], win: 'GWindow'):
    i = 0

    while i < len(l):
        if l[i].id == win.id:
            l.pop(i)
            continue

        i += 1


UpdateType = Callable[[list['GWindow']], Coroutine]


class Tracker:
    def __init__(
        self,
        tiler: type[Extension],
        ctx: 'Ctx',
        updateFn: str,
        args: dict,
        customEvents: list['Event'],
        ext: Extension,  # a hack to make the tracker destroyable lol
    ):
        self.ctx: 'Ctx' = ctx
        self.exts: dict[GDisplay, Extension] = {}
        self.updates: dict[GDisplay, UpdateType] = {}
        self.focusQueue: list[GWindow] = [
            win for win in ctx.windows.values() if ctx.editable(win)
        ]

        ext.addListener(mapRequest, self.mapWindow)
        ext.addListener(destroyNotify, self.destroyNotify)
        ext.addListener(focusChange, self.focusChange)
        ext.addListener(unmapNotify, self.unmapWindow)
        ext.addListener(mapNotify, self.mapNotify)
        ext.addListener(configureNotify, self.confNotify)

        for event in customEvents:
            ext.addListener(event, lambda *a: self.update())

        for display in ctx.screen.displays:
            ext = tiler(ctx, {**args, 'display': display})
            self.exts[display] = ext
            self.updates[display] = getattr(ext, updateFn)

    async def findFocus(self):
        # just having a focused win is not enough here!!
        if (
            self.ctx.focused
            and self.ctx.focused.mapped
            and not self.ctx.focused.destroyed
        ):
            await self.update()
            return

        for win in self.focusQueue:
            if self.ctx.editable(win) and not win.focused:
                await win.setFocus(True)
                return

    async def update(self):
        ordered: dict['GDisplay', list['GWindow']] = {}

        for dpy, wins in perDisplay(self.ctx, self.focusQueue).items():
            for win in wins:
                if not self.ctx.editable(win):
                    continue

                ordered[dpy] = [*ordered.get(dpy, []), win]

        for dpy, queue in ordered.items():
            await self.updates[dpy](queue.copy())

    async def unmapWindow(self, win: 'GWindow'):
        if self.ctx.focused and win.id == self.ctx.focused.id:
            await self.findFocus()
            return  # the update func is gonna be called if we find a win, and if we dont - there are no wins

        await self.update()

    async def confNotify(self, win: 'GWindow'):
        # ? should we do something more complex here?
        await self.update()

    async def mapNotify(self, win: 'GWindow'):
        if win.ignore:
            return

        await win.setFocus(True)
        # ? can the window be focused if its not mapped? (it shouldnt but idk)

    async def mapWindow(self, win: 'GWindow'):
        if win.ignore:
            return

        # this is a bit of a hack to get windows to be on the correct screen
        x, y = self.ctx.mouse.location()

        win.x = x
        win.y = y

        await win.map()  # This will set its focus, so we shouldn't need a focus change
        await self.update()

    async def destroyNotify(self, win: 'GWindow'):
        removeAll(self.focusQueue, win)

        await self.findFocus()

    async def focusChange(self, old: 'GWindow | None', new: 'GWindow | None'):
        for win in [old, new]:
            if win:
                removeAll(self.focusQueue, win)
                self.focusQueue.append(win)

        await self.update()
