from xcb_cffi import ffi, lib
from .types import chararr, uintarr
from ..generic import GButton, GMouse

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..generic import GWindow, GMod
    from ...ctx import Ctx

cursors = {
    "X_cursor": 0,
    "arrow": 2,
    "based_arrow_down": 4,
    "based_arrow_up": 6,
    "boat": 8,
    "bogosity": 10,
    "bottom_left_corner": 12,
    "bottom_right_corner": 14,
    "bottom_side": 16,
    "bottom_tee": 18,
    "box_spiral": 20,
    "center_ptr": 22,
    "circle": 24,
    "clock": 26,
    "coffee_mug": 28,
    "cross": 30,
    "cross_reverse": 32,
    "crosshair": 34,
    "diamond_cross": 36,
    "dot": 38,
    "dotbox": 40,
    "double_arrow": 42,
    "draft_large": 44,
    "draft_small": 46,
    "draped_box": 48,
    "exchange": 50,
    "fleur": 52,
    "gobbler": 54,
    "gumby": 56,
    "hand1": 58,
    "hand2": 60,
    "heart": 62,
    "icon": 64,
    "iron_cross": 66,
    "left_ptr": 68,
    "left_side": 70,
    "left_tee": 72,
    "leftbutton": 74,
    "ll_angle": 76,
    "lr_angle": 78,
    "man": 80,
    "middlebutton": 82,
    "mouse": 84,
    "pencil": 86,
    "pirate": 88,
    "plus": 90,
    "question_arrow": 92,
    "right_ptr": 94,
    "right_side": 96,
    "right_tee": 98,
    "rightbutton": 100,
    "rtl_logo": 102,
    "sailboat": 104,
    "sb_down_arrow": 106,
    "sb_h_double_arrow": 108,
    "sb_left_arrow": 110,
    "sb_right_arrow": 112,
    "sb_up_arrow": 114,
    "sb_v_double_arrow": 116,
    "shuttle": 118,
    "sizing": 120,
    "spider": 122,
    "spraycan": 124,
    "star": 126,
    "target": 128,
    "tcross": 130,
    "top_left_arrow": 132,
    "top_left_corner": 134,
    "top_right_corner": 136,
    "top_side": 138,
    "top_tee": 140,
    "trek": 142,
    "ul_angle": 144,
    "umbrella": 146,
    "ur_angle": 148,
    "watch": 150,
    "xterm": 152,
}  # stole this from qtile


class Mouse(GMouse):
    def __init__(self, ctx: 'Ctx') -> None:
        self.ctx = ctx

    def location(self) -> tuple[int, int]:
        resp = lib.xcb_query_pointer_reply(
            self.ctx.connection,
            lib.xcb_query_pointer(self.ctx.connection, self.ctx._root),
            ffi.NULL,
        )

        return (
            resp.root_x,
            resp.root_y,
        )  # ? idk if these are the values i need to return lol

    def setCursor(
        self,
        window: 'GWindow',
        _font: str,
        name: str,
        fore: int = 0,
        back: int = 0xFFFFFF,
    ):
        cursorId = cursors[name]

        font = lib.xcb_generate_id(self.ctx.connection)

        lib.xcb_open_font(
            self.ctx.connection,
            font,
            len(_font),
            chararr(_font.encode()),
        )

        cursor = lib.xcb_generate_id(self.ctx.connection)

        lib.xcb_create_glyph_cursor(
            self.ctx.connection,
            cursor,
            font,
            font,
            cursorId,
            cursorId + 1,
            (fore >> 16) % 256,
            (fore >> 8) % 256,
            fore % 256,
            (back >> 16) % 256,
            (back >> 8) % 256,
            back % 256,
        )

        mask = lib.XCB_CW_CURSOR
        args = uintarr([cursor])
        lib.xcb_change_window_attributes_checked(
            self.ctx.connection, window.id, mask, args
        )

        lib.xcb_close_font(self.ctx.connection, font)
        lib.xcb_free_cursor(self.ctx.connection, cursor)

        lib.xcb_flush(self.ctx.connection)


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
