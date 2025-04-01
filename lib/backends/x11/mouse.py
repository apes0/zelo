from typing import TYPE_CHECKING

from lib.backends.x11 import requests

from .. import xcb
from ..generic import GButton, GMouse, applyPre
from .keys import Key, Mod
from .types import chararr, uintarr

if TYPE_CHECKING:
    from ...ctx import Ctx
    from ..generic import GMod, GWindow
    from .gctx import Ctx as GCtx

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


@applyPre
class Mouse(GMouse):
    def __init__(self, ctx: 'Ctx') -> None:
        self.ctx = ctx

    async def location(self) -> tuple[int, int]:
        assert not self.ctx.closed, 'conn is closed'

        gctx: GCtx = self.ctx._getGCtx()

        resp = await requests.QueryPointer(
            self.ctx, gctx.connection, self.ctx._root
        ).reply()

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
        assert not self.ctx.closed, 'conn is closed'

        gctx: GCtx = self.ctx._getGCtx()

        cursorId = cursors[name]

        font = xcb.xcbGenerateId(gctx.connection)

        xcb.xcbOpenFont(
            gctx.connection,
            font,
            len(_font),
            chararr(_font.encode()),
        )

        cursor = xcb.xcbGenerateId(gctx.connection)

        xcb.xcbCreateGlyphCursor(
            gctx.connection,
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
        xcb.xcbChangeWindowAttributesChecked(gctx.connection, window.id, mask, args)

        xcb.xcbCloseFont(gctx.connection, font)
        xcb.xcbFreeCursor(gctx.connection, cursor)

        xcb.xcbFlush(gctx.connection)


mappings = {
    'any': xcb.XCBButtonIndexAny,
    'left': xcb.XCBButtonIndex1,
    'right': xcb.XCBButtonIndex2,
    'middle': xcb.XCBButtonIndex3,
    'scroll_up': xcb.XCBButtonIndex4,
    'scroll_down': xcb.XCBButtonIndex5,
}


@applyPre
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
        assert not ctx.closed, 'conn is closed'

        gctx: GCtx = ctx._getGCtx()

        mod = 0
        for _mod in mods:
            mod |= _mod.mod

        xcb.xcbGrabButton(
            gctx.connection,
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

        xcb.xcbFlush(gctx.connection)

    def ungrab(self, ctx: 'Ctx', window: 'GWindow', *mods: 'GMod'):
        assert not ctx.closed, 'conn is closed'

        gctx: GCtx = ctx._getGCtx()

        mod = 0
        for _mod in mods:
            mod |= _mod.mod

        xcb.xcbUngrabButton(
            gctx.connection,
            self.button,
            window.id,
            mod,
        )

        xcb.xcbFlush(gctx.connection)

    def press(self, ctx: 'Ctx', window: 'GWindow', x: int, y: int, *modifiers: Mod):
        assert not ctx.closed, 'conn is closed'

        gctx: GCtx = ctx._getGCtx()

        for mod in modifiers:
            Key(code=mod.mappings[mod.mod][0]).press(ctx, window, flush=False)

        xcb.xcbTestFakeInput(
            gctx.connection,
            xcb.XCBButtonPress,
            self.button,
            xcb.XCBCurrentTime,
            ctx._root,
            x,
            y,
            0,
        )

        xcb.xcbFlush(gctx.connection)

    def release(self, ctx: 'Ctx', window: 'GWindow', x: int, y: int, *modifiers: Mod):
        assert not ctx.closed, 'conn is closed'

        gctx: GCtx = ctx._getGCtx()

        for mod in modifiers:
            Key(code=Mod.mappings[mod.mod][0]).release(ctx, window, flush=False)

        xcb.xcbTestFakeInput(
            gctx.connection,
            xcb.XCBButtonRelease,
            self.button,
            xcb.XCBCurrentTime,
            ctx._root,
            x,
            y,
            0,
        )

        xcb.xcbFlush(gctx.connection)

    def __hash__(self) -> int:
        return hash(self.lable)
