# A class for tilers to use, because its really annoying to keep track of windows
# NOTE: i literally made this just because of the workspaces hah

from logging import DEBUG
from lib.debcfg import log
from utils.fns import getDisplay
from lib.extension import Extension
from lib.backends.events import mapRequest, destroyNotify, focusChange, unmapNotify, mapNotify, configureNotify

from typing import TYPE_CHECKING, Callable, Coroutine

if TYPE_CHECKING:
    from lib.ctx import Ctx
    from lib.backends.generic import GWindow, GDisplay
    from lib.backends.events import Event


def track(updateFn: str, custom: list = []):
    def deco(ext: type[Extension]):
        class New:
            def __init__(self, ctx: 'Ctx', args: dict) -> None:
                Tracker(ext, ctx, updateFn, args, custom)

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
        customEvents: list['Event'] = [],
    ):
        self.ctx: 'Ctx' = ctx
        self.exts: dict[GDisplay, Extension] = {}
        self.updates: dict[GDisplay, UpdateType] = {}
        self.focusQueue: list[GWindow] = [
            win for win in ctx.windows.values() if win.mapped and not win.ignore
        ]

        for display in ctx.screen.displays:
            ext = tiler(ctx, {**args, 'display': display})
            self.exts[display] = ext
            self.updates[display] = getattr(ext, updateFn)

        mapRequest.addListener(self.mapWindow)
        destroyNotify.addListener(self.destroyNotify)
        focusChange.addListener(self.focusChange)
        unmapNotify.addListener(self.unmapWindow)
        mapNotify.addListener(self.mapNotify)
        configureNotify.addListener(self.confNotify)

        for event in customEvents:
            event.addListener(lambda *a: self.update())

    async def findFocus(self):
        # just having a focused win is not enough here!!
        if self.ctx.focused and self.ctx.focused.mapped and not self.ctx.focused.destroyed:
            await self.update()
            return

        for win in self.focusQueue:
            if not win.ignore and not win.focused and win.mapped:
                await win.setFocus(True)
                return

    async def update(self):
        ordered: dict['GDisplay', list['GWindow']] = {}

        for dpy, wins in perDisplay(self.ctx, self.focusQueue).items():
            for win in wins:
                if not win.mapped or win.ignore or win.id == self.ctx._root:
                    continue

                ordered[dpy] = [*ordered.get(dpy, []), win]

        for dpy, queue in ordered.items():
            await self.updates[dpy](queue.copy())

    async def unmapWindow(self, win: 'GWindow'):
        if self.ctx.focused and win.id == self.ctx.focused.id:
            await self.findFocus()
            return # the update func is gonna be called if we find a win, and if we dont - there are no wins
        
        await self.update()

    async def confNotify(self, win: 'GWindow'):
        #? should we do something more complex here?
        await self.update()

    async def mapNotify(self, win: 'GWindow'):
        if win.ignore:
            return

        await win.setFocus(True)
        #? can the window be focused if its not mapped? (it shouldnt but idk)

    async def mapWindow(self, win: 'GWindow'):
        if win.ignore:
            return

        # this is a bit of a hack to get windows to be on the correct screen
        x, y = self.ctx.mouse.location()

        win.x = x
        win.y = y

        await win.map() # This will set its focus, so we shouldn't need a focus change
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
