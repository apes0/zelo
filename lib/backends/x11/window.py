from ..generic import GWindow
from xcb_cffi import ffi, lib
from .types import uintarr
from typing import TYPE_CHECKING
from ...cfg import cfg
from ..events import focusChange

if TYPE_CHECKING:
    from ...ctx import Ctx


class Window(GWindow):
    def __init__(self, height, width, borderWidth, _id, ctx: 'Ctx') -> None:
        self.height: int = height
        self.width: int = width
        self.borderWidth: int = borderWidth
        self.x: int = 0
        self.y: int = 0
        self.id = _id
        self.ctx: 'Ctx' = ctx
        self.parent: Window | None = None
        self.focused: bool = False
        self.mapped: bool = False
        self.ignore = True  # set by override redirect (also we assume the worst, so we set it to true)

    def map(self):
        lib.xcb_map_window(self.ctx.connection, self.id)
        lib.xcb_flush(self.ctx.connection)
        self.mapped = True

    def unmap(self):
        lib.xcb_unmap_window(self.ctx.connection, self.id)
        lib.xcb_flush(self.ctx.connection)
        self.mapped = False

    def setFocus(self, focus: bool):
        # print(
        #    self.id,
        #    self.ctx.focused,
        #    None if self.ctx.focused is None else self.ctx.focused.id,
        #    focus,
        # )
        self.focused = focus
        color = cfg.unfocusedColor
        if focus:
            color = cfg.focusedColor
            lib.xcb_set_input_focus(
                self.ctx.connection,
                lib.XCB_INPUT_FOCUS_POINTER_ROOT,  # seemingly fine?
                self.id,
                lib.XCB_CURRENT_TIME,
            )

            if not self.ctx.focused:
                # print(f'focus on {self.id}, current: {None}')
                self.ctx.focused = self
                focusChange.trigger(self.ctx, None, self)

            elif self.ctx.focused.id != self.id:
                # print(f'focus on {self.id}, current: {self.ctx.focused.id}')
                old: GWindow = self.ctx.focused
                old.setFocus(False)
                self.ctx.focused = self

                focusChange.trigger(self.ctx, old, self)

        else:
            # if the id of the focused is our id, and only then, we need to unfocus the window,
            # otherwise, if the ids arent the same, then we are already unfocused
            if self.ctx.focused and self.ctx.focused.id == self.id:
                # print(f'unfocus on {self.id}')
                self.ctx.focused = None
                focusChange.trigger(self.ctx, self, None)

        lib.xcb_change_window_attributes_checked(
            self.ctx.connection, self.id, lib.XCB_CW_BORDER_PIXEL, uintarr([color])
        )

        lib.xcb_flush(self.ctx.connection)

    def configure(
        self,
        newX: int | None = None,
        newY: int | None = None,
        newWidth: int | None = None,
        newHeight: int | None = None,
        newBorderWidth: int | None = None,
    ):
        compare = {
            (newX, 'x'): lib.XCB_CONFIG_WINDOW_X,
            (newY, 'y'): lib.XCB_CONFIG_WINDOW_Y,
            (newWidth, 'width'): lib.XCB_CONFIG_WINDOW_WIDTH,
            (newHeight, 'height'): lib.XCB_CONFIG_WINDOW_HEIGHT,
            (newBorderWidth, 'borderWidth'): lib.XCB_CONFIG_WINDOW_BORDER_WIDTH,
        }

        vals = []
        changed = 0
        new: int | None
        for (new, currentName), change in compare.items():
            if not new:  # check if it was set as an argument
                continue
            new = max(0, new)  # if its negative, it will not work with ``uint``
            current = self.__dict__[currentName]
            if new != current:
                changed |= change
                vals.append(new)
                self.__dict__[currentName] = new

        vals = uintarr(vals)

        if not changed:
            return  # ? does this break shit - limp bizkit?

        lib.xcb_configure_window(
            self.ctx.connection,
            self.id,
            changed,
            vals,
        )

        lib.xcb_flush(self.ctx.connection)

    def close(self):
        lib.xcb_kill_client(self.ctx.connection, self.id)
        lib.xcb_flush(self.ctx.connection)
