from lib.extension import Extension
from typing import TYPE_CHECKING
from .windowTracker import Tracker
from lib.backends.events import focusChange

if TYPE_CHECKING:
    from lib.ctx import Ctx
    from lib.backends.generic import GWindow

# tiles windows in the following way:
#
# the main window takes up ``mainSize`` of the screen horizontally if there are no secondary
# windows, else it takes up the whole screen, and goes to the bottom of the screen (not including
# the spacing between windows)
# the secondary windows take up ``1 - mainSize`` of the screen horizontally, and are equally spaced
# vertically, taking up ``1 / max(secondaryWindows, 1)`` of the screen vertically (not including the
# spacing between windows)
# Main window only:
# _____________________________________________________
# |                                                   |
# | main window                                       |
# |___________________________________________________|
#
# With multiple window:
# _____________________________________________________
# |                               |_secondary_windows_|
# | main window                   |___________________|
# |_______________________________|___________________|
#
# the main window is the currently focused window

# FIXME: breaks with too many windows (its an unreasonable number imho, but we should handle it properly)


class Tiler(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        super().__init__(ctx, cfg)
        self.mainSize: int
        self.border: int
        self.spacing: int
        Tracker(self, self.update, [focusChange])

    def update(self, windows: dict[int, 'GWindow']):
        main: GWindow | None = self.ctx.focused

        if not main:  # cant have secondary windows if there isnt a main one
            return
        if main.id in windows:
            del windows[main.id]

        size = 1 / max(len(windows), 1)
        y = self.spacing
        _height = self.ctx.screen.height * size - (2 + size) * self.spacing
        height = round(_height)
        offset = _height - height
        width = round(self.ctx.screen.width * (1 - self.mainSize) - self.spacing * 3)
        x = round(self.ctx.screen.width * self.mainSize + self.spacing)

        for window in windows.values():
            window.configure(
                newX=x,
                newY=round(y),
                newHeight=height,
                newWidth=width,
                newBorderWidth=self.border,
            )
            y += height + self.spacing * 2 + offset

        mainSize = self.mainSize if windows else 1
        main.configure(
            newX=self.spacing,
            newY=self.spacing,
            newWidth=round(self.ctx.screen.width * mainSize - 3 * self.spacing),
            newHeight=self.ctx.screen.height - 3 * self.spacing,
            newBorderWidth=self.border,
        )
