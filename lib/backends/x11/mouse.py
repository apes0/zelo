from xcb_cffi import ffi, lib
from ..generic import GButton

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..generic import GWindow, GMod
    from ...ctx import Ctx

mappings = {
    'any': lib.XCB_BUTTON_INDEX_ANY,
    'left': lib.XCB_BUTTON_INDEX_1,
    'right': lib.XCB_BUTTON_INDEX_2,
    'middle': lib.XCB_BUTTON_INDEX_3,
    'scroll_up': lib.XCB_BUTTON_INDEX_4,
    'scroll_down': lib.XCB_BUTTON_INDEX_5,
}


class Button(GButton):
    def __init__(self, lable: str | None = None, button: int | None = None) -> None:
        self.lable: str
        self.button: int

        assert (
            lable is not None or button is not None
        ), 'You must set the name of the button or the button code.'
        if lable:
            self.lable = lable
            self.button = mappings[lable]
        else:
            self.button = button  # type:ignore
            for lable, key in mappings.items():
                if key == button:
                    self.lable = lable
                    break

    def grab(self, ctx: 'Ctx', window: 'GWindow', *mods: 'GMod'):
        mod = 0
        for _mod in mods:
            mod |= _mod.mod

        lib.xcb_grab_button(
            ctx.connection,
            0,
            window.id,
            lib.XCB_EVENT_MASK_BUTTON_PRESS,
            lib.XCB_GRAB_MODE_ASYNC,
            lib.XCB_GRAB_MODE_ASYNC,
            lib.XCB_NONE,
            0,
            self.button,
            mod,
        )

        lib.xcb_flush(ctx.connection)

    def ungrab(self, ctx: 'Ctx', window: 'GWindow', *mods: 'GMod'):
        mod = 0
        for _mod in mods:
            mod |= _mod.mod

        lib.xcb_ungrab_button(
            ctx.connection,
            self.button,
            window.id,
            mod,
        )

        lib.xcb_flush(ctx.connection)

    def __hash__(self) -> int:
        return hash(self.lable)
