from lib.extension import Extension
from typing import TYPE_CHECKING
from .windowTracker import track

if TYPE_CHECKING:
    from lib.ctx import Ctx
    from lib.backends.generic import GWindow, GDisplay

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
# FIXME: breaks with spacing of 0


@track('update')
class Tiler(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.mainSize: float
        self.border: int
        self.spacing: int
        self.display: GDisplay

        super().__init__(ctx, cfg, resolve={'border': int, 'spacing': int})

    async def update(self, windows: list['GWindow']):
        main: 'GWindow' = windows.pop()  # this doesnt error for some reason?

        size = 1 / max(
            len(windows), 1
        )  # get the size of the side windows as a fraction
        y = self.spacing  # start the y coordinate at ``self.spacing`` pixels down
        _height = (
            self.display.height * size - (2 + size) * self.spacing
        )  # calculate the height of each side window
        height = round(_height)  # round it to a whole number
        offset = _height - height  # get the error from the rounded version
        width = round(
            self.display.width * (1 - self.mainSize) - self.spacing * 3
        )  # calculate the width of every side window
        x = round(
            self.display.width * self.mainSize + self.spacing
        )  # calculate the x coordinate of the side windows

        for window in windows:
            await window.configure(
                newX=x + self.display.x,
                newY=round(y) + self.display.y,
                newHeight=height,
                newWidth=width,
                newBorderWidth=self.border,
            )
            y += height + self.spacing * 2 + offset

        mainSize = self.mainSize if windows else 1
        await main.configure(
            newX=self.spacing + self.display.x,
            newY=self.spacing + self.display.y,
            newWidth=round(self.display.width * mainSize - 3 * self.spacing),
            newHeight=self.display.height - 3 * self.spacing,
            newBorderWidth=self.border,
        )

        # multiple is broken here hh
