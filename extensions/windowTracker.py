# A class for tilers to use, because its really annoying to keep track of windows
# NOTE: i literally made this just because of the workspaces hah

from lib.extension import Extension
from lib.backends.events import mapRequest, unmapNotify, destroyNotify, focusChange

from collections import deque
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from lib.ctx import Ctx
    from lib.backends.generic import GWindow
    from lib.backends.events import Event


class Tracker:
    def __init__(
        self,
        tiler: Extension,
        updateFn: Callable[[dict[int, 'GWindow']], None],
        customEvents: list['Event'] = [],
    ):
        self.ctx: 'Ctx' = tiler.ctx
        self._update: Callable[[dict[int, 'GWindow']], None] = updateFn
        self.windows: list['GWindow'] = []
        self.queue: deque['GWindow'] = deque()

        mapRequest.addListener(self.mapWindow)
        unmapNotify.addListener(self.unmapWindow)
        destroyNotify.addListener(self.destroyNotify)
        focusChange.addListener(self.focusChange)

        for event in customEvents:
            event.addListener(lambda *a: self.update())

    def update(self):
        windows: dict[int, GWindow] = {}
        window: GWindow
        for id, window in self.ctx.windows.items():
            if not window.mapped:
                continue
            windows[id] = window
        self._update(windows)

    def mapWindow(self, window: 'GWindow'):
        if not window.mapped:
            self.queue.append(window)
            window.map()
            window.setFocus(True)
            self.update()

    def unmapWindow(self, _window: 'GWindow'):
        if not self.ctx.focused:
            while self.queue and (window := self.queue.pop()):
                if window.mapped:
                    window.setFocus(True)
                    break
        self.update()

    def destroyNotify(self, _window: 'GWindow'):
        if not self.ctx.focused:
            while self.queue and (window := self.queue.pop()):
                if window.mapped:
                    window.setFocus(True)
                    break
        self.update()

    def focusChange(self, old: 'GWindow | None', new: 'GWindow | None'):
        if old and old.mapped and new is not None:
            self.queue.append(old)
