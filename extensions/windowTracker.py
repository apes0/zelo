# A class for tilers to use, because its really annoying to keep track of windows
# NOTE: i literally made this just because of the workspaces hah

from lib.extension import Extension
from lib.backends.events import mapRequest, destroyNotify, focusChange

from typing import TYPE_CHECKING, Callable

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


UpdateType = Callable[[dict[int, 'GWindow'], 'GWindow'], None]


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
        self.mains = {}
        self.focusQueue: list[GWindow] = []

        for display in ctx.screen.displays:
            ext = tiler(ctx, {**args, 'display': display})
            self.exts[display] = ext
            self.updates[display] = getattr(ext, updateFn)

        mapRequest.addListener(self.mapWindow)
        destroyNotify.addListener(self.destroyNotify)
        focusChange.addListener(self.focusChange)

        for event in customEvents:
            event.addListener(lambda *a: self.update())

    def findMain(self, dpy: 'GDisplay'):
        for window in self.focusQueue:
            if (
                getDisplay(self.ctx, window.x, window.y) == dpy
                and not window.ignore
                and window.mapped
            ):
                return window

    def update(self):
        windows: dict[GDisplay, dict[int, GWindow]] = {}

        for win in self.ctx.windows.values():
            if not win.mapped or win.ignore or win.id == self.ctx._root:
                continue

            dpy = getDisplay(self.ctx, win.x, win.y)

            if not dpy:
                continue

            windows[dpy] = {**windows.get(dpy, {}), win.id: win}

        for dpy, update in self.updates.items():
            if main := self.mains.get(dpy):
                if main.ignore or not main.mapped:
                    main = self.findMain(dpy)
                    self.mains[dpy] = main
                    if not main:
                        continue

                    main.setFocus(True)

                update(windows.get(dpy, {}), main)

    async def mapWindow(self, win: 'GWindow'):
        if not win.mapped:
            win.map()
            win.setFocus(True)

            # this is a bit of a hack to get windows to be on the correct screen
            x, y = self.ctx.mouse.location()
            dpy = getDisplay(self.ctx, x, y)

            if (
                not dpy
            ):  # never should happen, but just in case it does, this is here (also it makes pylances top complaining)
                return

            self.mains[dpy] = win

            win.x = dpy.x  # kinda a hack
            win.y = dpy.y
        self.update()

    async def destroyNotify(self, win: 'GWindow'):
        dpy = getDisplay(self.ctx, win.x, win.y)
        if dpy:  # aways gonna happen i assume, but idk
            if self.mains.get(dpy) and win.id == self.mains[dpy].id:
                new = self.findMain(dpy)
                self.mains[dpy] = new
                if new:
                    new.setFocus(True)

        if win in self.focusQueue:
            self.focusQueue.remove(win)
        self.update()

    async def focusChange(self, old: 'GWindow | None', new: 'GWindow | None'):
        if old:
            if old in self.focusQueue:
                self.focusQueue.remove(old)
            self.focusQueue.append(old)

        if new:
            newDpy = getDisplay(self.ctx, new.x, new.y)
            if newDpy:
                self.mains[newDpy] = new

        self.update()
