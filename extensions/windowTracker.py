# A class for tilers to use, because its really annoying to keep track of windows
# NOTE: i literally made this just because of the workspaces hah

from lib.extension import Extension
from lib.backends.events import mapRequest, unmapNotify, destroyNotify, focusChange

from collections import deque
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
        self.queues: dict[GDisplay, deque['GWindow']] = {}

        for display in ctx.screen.displays:
            ext = tiler(ctx, {**args, 'display': display})
            self.exts[display] = ext
            self.updates[display] = getattr(ext, updateFn)
            self.queues[display] = deque()

        mapRequest.addListener(self.mapWindow)
        unmapNotify.addListener(self.unmapWindow)
        destroyNotify.addListener(self.destroyNotify)
        focusChange.addListener(self.focusChange)

        for event in customEvents:
            event.addListener(lambda *a: self.update())

    def update(self):
        windows: dict[GDisplay, dict[int, GWindow]] = {}
        window: GWindow
        for id, window in self.ctx.windows.items():
            display = getDisplay(self.ctx, window.x, window.y)
            if not window.mapped or window.ignore or not display:
                continue
            windows[display] = {**windows.get(display, {}), window.id: window}

        for display, _windows in windows.items():
            main = self.mains.get(display)
            # if there is no root, there are no secondaries
            if not main:
                continue
            self.updates[display](_windows, main)

    def mapWindow(self, window: 'GWindow'):
        if not window.mapped:
            # this is a bit of a hack to get windows to be on the correct screen
            x, y = self.ctx.mouse.location()
            print(x, y)
            display = getDisplay(self.ctx, x, y)

            if (
                not display
            ):  # never should happen, but just in case it does, this is here (also it makes pylance stop complaining)
                return

            window.x = display.x
            window.y = display.y

            self.queues[display].append(window)
            window.map()
            window.setFocus(True)
            self.mains[display] = window
            self.update()

    def unmapWindow(self, _window: 'GWindow'):
        display = getDisplay(self.ctx, _window.x, _window.y)

        if not display:
            return

        queue: deque[GWindow] = self.queues[display]

        if not self.ctx.focused:
            while queue and (window := queue.pop()):
                if window.mapped:
                    window.setFocus(True)
                    break
        self.update()

    def destroyNotify(self, _window: 'GWindow'):
        display = getDisplay(self.ctx, _window.x, _window.y)

        if not display:
            return

        queue: deque[GWindow] = self.queues[display]

        if not self.ctx.focused:
            while queue and (window := queue.pop()):
                if window.mapped:
                    window.setFocus(True)
                    break
        self.update()

    def focusChange(self, old: 'GWindow | None', new: 'GWindow | None'):
        if old:
            oldDisplay = getDisplay(self.ctx, old.x, old.y)
            if oldDisplay:
                self.mains[oldDisplay] = None

        if new and not new.ignore:
            newDisplay = getDisplay(self.ctx, new.x, new.y)
            if newDisplay:
                self.mains[newDisplay] = new

        if old and old.mapped and new is not None:
            oldDisplay = getDisplay(self.ctx, old.x, old.y)
            if oldDisplay:
                self.queues[oldDisplay].append(old)

        self.update()
