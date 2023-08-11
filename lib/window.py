from .ffi import lib as xcb
from .types import uintarr
from typing import TYPE_CHECKING
from .cfg import focusedColor, unfocusedColor

if TYPE_CHECKING:
    from .ctx import Ctx


class Window:
    def __init__(self, height, width, borderWidth, _id, ctx: 'Ctx') -> None:
        self.height = height
        self.width = width
        self.borderWidth = borderWidth
        self.x: int = 0
        self.y: int = 0
        self.id = _id
        self.ctx: 'Ctx' = ctx
        self.focused = False

    def setFocus(self, focus):
        self.focused = focus
        color = unfocusedColor
        if focus:
            color = focusedColor
            xcb.xcb_set_input_focus(
                self.ctx.connection,
                xcb.XCB_INPUT_FOCUS_POINTER_ROOT,  # seemingly fine?
                self.id,
                xcb.XCB_CURRENT_TIME,
            )
            self.ctx.focused.setFocus(False)
            self.ctx.focused = self

        xcb.xcb_change_window_attributes_checked(
            self.ctx.connection, self.id, xcb.XCB_CW_BORDER_PIXEL, uintarr([color])
        )

        xcb.xcb_flush(self.ctx.connection)

    def configure(
        self, newX=None, newY=None, newWidth=None, newHeight=None, newBorderWidth=None
    ):
        compare = {
            (newX, 'x'): xcb.XCB_CONFIG_WINDOW_X,
            (newY, 'y'): xcb.XCB_CONFIG_WINDOW_Y,
            (newWidth, 'width'): xcb.XCB_CONFIG_WINDOW_WIDTH,
            (newHeight, 'height'): xcb.XCB_CONFIG_WINDOW_HEIGHT,
            (newBorderWidth, 'borderWidth'): xcb.XCB_CONFIG_WINDOW_BORDER_WIDTH,
        }

        vals = []
        changed = 0
        for (new, currentName), change in compare.items():
            new = max(0, new)  # type:ignore
            current = self.__dict__[currentName]
            if new != current and new is not None:
                changed |= change
                vals.append(new)
                self.__dict__[currentName] = new

        vals = uintarr(vals)

        if not changed:
            return  # ? does this break shit - limp bizkit?

        xcb.xcb_configure_window(
            self.ctx.connection,
            self.id,
            changed,
            vals,
        )

        xcb.xcb_flush(self.ctx.connection)
