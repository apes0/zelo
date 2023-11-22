# A class for tilers to use, because its really annoying to keep track of windows
# NOTE: i literally made this just because of the workspaces hah

from lib.extension import Extension
from lib.backends.events import mapRequest, unmapNotify, destroyNotify, focusChange

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
        self.windows = []  # i prefer a list here rather than a dequeue

        for display in ctx.screen.displays:
            ext = tiler(ctx, {**args, 'display': display})
            self.exts[display] = ext
            self.updates[display] = getattr(ext, updateFn)

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
            display = getDisplay(self.ctx, x, y)

            if (
                not display
            ):  # never should happen, but just in case it does, this is here (also it makes pylance stop complaining)
                return

            window.x = display.x  # kinda a hack
            window.y = display.y

            self.windows.append(window)
            window.map()
            window.setFocus(True)

            if not window.ignore:
                self.mains[display] = window
                print(window.id, 1)

            self.update()

    def unmapWindow(self, _window: 'GWindow'):
        if _window.parent:
            self.mains[
                getDisplay(self.ctx, _window.parent.x, _window.parent.y)
            ] = _window.parent
            print(_window.parent.id, 2)
            _window.parent.setFocus(True)
            self.update()
            return

        window = None

        if not self.ctx.focused:
            for window in self.windows:
                if window.mapped:
                    window.setFocus(True)
                    break

        dpy = getDisplay(self.ctx, _window.x, _window.y)

        if not dpy:
            return

        for window in self.windows:
            if (
                getDisplay(self.ctx, window.x, window.y) == dpy
                and not window.ignore
                and window.mapped
            ):
                self.mains[dpy] = window
                print(window.id, 3)
                break

        self.update()

    def destroyNotify(self, _window: 'GWindow'):
        print(_window.id)
        if _window.parent and _window.parent != self.ctx.root:
            self.mains[
                getDisplay(self.ctx, _window.parent.x, _window.parent.y)
            ] = _window.parent
            print(_window.parent.id, 4)
            _window.parent.setFocus(True)
            self.update()
            return

        if not self.ctx.focused:
            for window in self.windows:
                if window.mapped:
                    window.setFocus(True)
                    break

        dpy = getDisplay(self.ctx, _window.x, _window.y)

        if not dpy:
            return

        if not self.mains[dpy]:
            for window in self.windows:
                if (
                    getDisplay(self.ctx, window.x, window.y) == dpy
                    and not window.ignore
                    and window.mapped
                ):
                    self.mains[dpy] = window
                    print(window.id, 5)
                    break

        self.update()

    def focusChange(self, old: 'GWindow | None', new: 'GWindow | None'):
        if old:
            oldDisplay = getDisplay(self.ctx, old.x, old.y)
            if oldDisplay:
                self.mains[oldDisplay] = None
                print(None, 6)

        if new and not new.ignore:
            newDisplay = getDisplay(self.ctx, new.x, new.y)
            if newDisplay:
                self.mains[newDisplay] = new
                print(new.id, 7)

        if old and old.mapped and new is not None:
            self.windows.append(old)

        self.update()
