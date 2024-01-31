# A class for tilers to use, because its really annoying to keep track of windows
# NOTE: i literally made this just because of the workspaces hah

from lib.extension import Extension
from lib.backends.events import mapRequest, destroyNotify, focusChange, unmapNotify

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


def getDisplay(ctx: 'Ctx', x: int, y: int):
    display: GDisplay | None = None

    for _display in ctx.screen.displays:
        if x - _display.x < _display.width and y - _display.y < _display.height:
            display = _display
            break

    return display


def perDisplay(ctx: 'Ctx', wins: list['GWindow']):
    out: dict['GDisplay', list['GWindow']] = {}
    for win in wins:
        dpy = getDisplay(ctx, win.x, win.y)

        if not dpy:
            continue

        out[dpy] = [*out.get(dpy, []), win]

    return out


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
        self.focusQueue: list[GWindow] = []

        for display in ctx.screen.displays:
            ext = tiler(ctx, {**args, 'display': display})
            self.exts[display] = ext
            self.updates[display] = getattr(ext, updateFn)

        mapRequest.addListener(self.mapWindow)
        destroyNotify.addListener(self.destroyNotify)
        focusChange.addListener(self.focusChange)
        unmapNotify.addListener(self.unmapWindow)

        for event in customEvents:
            event.addListener(lambda *a: self.update())

    async def findFocus(self):
        if self.ctx.focused:
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
        dpy = getDisplay(self.ctx, win.x, win.y)
        if dpy:
            await self.findFocus()

        await self.update()

    async def mapWindow(self, win: 'GWindow'):
        if not win.mapped:
            await win.map()
            await win.setFocus(True)

            # this is a bit of a hack to get windows to be on the correct screen
            x, y = self.ctx.mouse.location()

            win.x = x  # kinda a hack
            win.y = y

        await self.update()

    async def destroyNotify(self, win: 'GWindow'):
        if win in self.focusQueue:
            self.focusQueue.remove(win)

        await self.findFocus()

        await self.update()

    async def focusChange(self, old: 'GWindow | None', new: 'GWindow | None'):
        for win in [old, new]:
            if win:
                if win in self.focusQueue:
                    self.focusQueue.remove(win)
                self.focusQueue.append(win)

        await self.update()
