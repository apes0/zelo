from .. import xcb
from .types import chararr, uintarr
from ..generic import GButton, GMouse

from logging import DEBUG
from ...debcfg import log

from .keys import Mod, Key

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
        resp = xcb.xcbQueryPointerReply(
            self.ctx.connection,
            xcb.xcbQueryPointer(self.ctx.connection, self.ctx._root),
            xcb.NULL,
        )

        return (
            resp.rootX,
            resp.rootY,
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

        font = xcb.xcbGenerateId(self.ctx.connection)

        xcb.xcbOpenFont(
            self.ctx.connection,
            font,
            len(_font),
            chararr(_font.encode()),
        )

        cursor = xcb.xcbGenerateId(self.ctx.connection)

        xcb.xcbCreateGlyphCursor(
            self.ctx.connection,
            cursor,
            font,
            font,
            cursorId,
            cursorId + 1,
            ((fore >> 16) % 256) * 257,
            ((fore >> 8) % 256) * 257,
            (fore % 256) * 257,
            ((back >> 16) % 256) * 257,
            ((back >> 8) % 256) * 257,
            (back % 256) * 257,
        )

        mask = xcb.XCBCwCursor
        args = uintarr([cursor])
        xcb.xcbChangeWindowAttributesChecked(self.ctx.connection, window.id, mask, args)

        xcb.xcbCloseFont(self.ctx.connection, font)
        xcb.xcbFreeCursor(self.ctx.connection, cursor)

        xcb.xcbFlush(self.ctx.connection)


mappings = {
    'any': xcb.XCBButtonIndexAny,
    'left': xcb.XCBButtonIndex1,
    'right': xcb.XCBButtonIndex2,
    'middle': xcb.XCBButtonIndex3,
    'scroll_up': xcb.XCBButtonIndex4,
    'scroll_down': xcb.XCBButtonIndex5,
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
        log('grab', DEBUG, f'grabbing {self} with modifiers {mods} on {window}')
        mod = 0
        for _mod in mods:
            mod |= _mod.mod

        xcb.xcbGrabButton(
            ctx.connection,
            0,
            window.id,
            xcb.XCBEventMaskButtonPress,
            xcb.XCBGrabModeAsync,
            xcb.XCBGrabModeAsync,
            xcb.XCBNone,
            0,
            self.button,
            mod,
        )

        xcb.xcbFlush(ctx.connection)

    def ungrab(self, ctx: 'Ctx', window: 'GWindow', *mods: 'GMod'):
        log('grab', DEBUG, f'ungrabbing {self} with modifiers {mods} on {window}')
        mod = 0
        for _mod in mods:
            mod |= _mod.mod

        xcb.xcbUngrabButton(
            ctx.connection,
            self.button,
            window.id,
            mod,
        )

        xcb.xcbFlush(ctx.connection)

    def press(self, ctx: 'Ctx', window: 'GWindow', x: int, y: int, *modifiers: Mod):
        log('press', DEBUG, f'pressing {self} with modifiers {modifiers}')

        for mod in modifiers:
            Key(code=mod.mappings[mod.mod][0]).press(ctx, window, flush=False)

        xcb.xcbTestFakeInput(
            ctx.connection,
            xcb.XCBButtonPress,
            self.button,
            xcb.XCBCurrentTime,
            ctx._root,
            x,
            y,
            0,
        )

        xcb.xcbFlush(ctx.connection)

    def release(self, ctx: 'Ctx', window: 'GWindow', x: int, y: int, *modifiers: Mod):
        log('press', DEBUG, f'releasing {self} with modifiers {modifiers}')

        for mod in modifiers:
            Key(code=Mod.mappings[mod.mod][0]).release(ctx, window, flush=False)

        xcb.xcbTestFakeInput(
            ctx.connection,
            xcb.XCBButtonRelease,
            self.button,
            xcb.XCBCurrentTime,
            ctx._root,
            x,
            y,
            0,
        )

        xcb.xcbFlush(ctx.connection)

    def __hash__(self) -> int:
        return hash(self.lable)
