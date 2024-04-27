from lib.extension import Extension
from typing import TYPE_CHECKING
from .windowTracker import track
from utils.fns import multiple

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
        self.topSpacing: int = 0
        self.bottomSpacing: int = 0
        self.leftSpacing: int = 0
        self.rightSpacing: int = 0
        self.display: GDisplay

        super().__init__(
            ctx,
            cfg,
            resolve={
                'border': int,
                'spacing': int,
                'topSpacing': int,
                'bottomSpacing': int,
                'leftSpacing': int,
                'rightSpacing': int,
            },
        )

        self.x = self.display.x + self.leftSpacing
        self.y = self.display.y + self.topSpacing
        self.width = self.display.width - self.leftSpacing - self.rightSpacing
        self.height = self.display.height - self.topSpacing - self.bottomSpacing

    async def update(self, windows: list['GWindow']):
        main: 'GWindow' = windows.pop()  # this doesnt error for some reason?

        size = 1 / max(
            len(windows), 1
        )  # get the size of the side windows as a fraction
        y = self.spacing  # start the y coordinate at ``self.spacing`` pixels down
        _height = (
            self.height - (1 + len(windows)) * (self.spacing) - 2*len(windows)*self.border
        )*size  # calculate the height of each side window
        height = round(_height)  # round it to a whole number
        offset = _height - height  # get the error from the rounded version
        width = round(
            self.width * (1 - self.mainSize) - self.spacing - 2 * self.border
        )  # calculate the width of every side window
        x = round(
            self.width * self.mainSize
        )  # calculate the x coordinate of the side windows

        fns = []

        for window in windows:
            fns.append(
                window.configure(
                    newX=x + self.x,
                    newY=round(y) + self.y,
                    newHeight=height,
                    newWidth=width,
                    newBorderWidth=self.border,
                )
            )
            y += height + self.spacing + offset + 2*self.border

        mainSize = self.mainSize if windows else 1
        fns.append(
            main.configure(
                newX=self.spacing + self.x,
                newY=self.spacing + self.y,
                newWidth=round(self.width * mainSize - 2 * self.spacing - 2 * self.border),
                newHeight=self.height - 2 * self.spacing - 2 * self.border,
                newBorderWidth=self.border,
            )
        )

        await multiple(*fns)
