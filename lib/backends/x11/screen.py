from ..generic import GDisplay, GScreen
from .types import chararr
from .. import xcb
from .requests import GetCrtcTransform, SetCrtcConfig

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...ctx import Ctx

# TODO: support xinerama as well (should not be difficult i hope)


class Display(GDisplay):
    def __init__(self, ctx: 'Ctx', x: int, y: int, width: int, height: int) -> None:
        self.ctx = ctx
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height
        self._crtc: int
        self._mode: int
        self._rotation: int
        self._outputs: Any
        self._numOutputs: int

    # TODO: check if randr is present for scale
    async def scale(self, x: float, y: float):
        # https://gitlab.freedesktop.org/xorg/app/xrandr/-/blob/master/xrandr.c?ref_type=heads#L3022

        filter = b'nearest' if round(x) == x and round(y) == y else b'bilinear'

        # https://github.com/winft/disman/blob/fdc697e27f28e45524ec146184ad61ed1de74062/backends/xrandr/xrandroutput.cpp#L459

        transform = await GetCrtcTransform(
            self.ctx, self.ctx.gctx.connection, self._crtc
        ).reply()

        t = transform.currentTransform
        t.matrix11 = xcb.doubleToFixed(1 / x)
        t.matrix22 = xcb.doubleToFixed(1 / y)
        t.matrix33 = xcb.doubleToFixed(1)

        xcb.xcbRandrSetCrtcTransform(
            self.ctx.gctx.connection,
            self._crtc,
            t,
            len(filter),
            chararr(filter),
            0,
            xcb.NULL,
        )

        r = await SetCrtcConfig(
            self.ctx,
            self.ctx.gctx.connection,
            self._crtc,
            xcb.XCBCurrentTime,
            xcb.XCBCurrentTime,
            self.x,
            self.y,
            self._mode,
            self._rotation,
            self._numOutputs,
            self._outputs,
        ).reply()

        xcb.xcbFlush(self.ctx.gctx.connection)

        transform = await GetCrtcTransform(
            self.ctx, self.ctx.gctx.connection, self._crtc
        ).reply()


class Screen(
    GScreen
):  # idk if wayland has an equivalent for rootDepth, so i wont put it here yet
    def __init__(self, screen) -> None:
        self.width: int = screen.widthInPixels
        self.height: int = screen.heightInPixels
        self.root: int = screen.root
        self.screen = screen
        self.displays: list[Display] = []
