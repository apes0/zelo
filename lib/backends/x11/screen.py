from ..generic import GDisplay, GScreen, pre, applyPre
from .types import chararr
from .. import xcb
from .requests import RandrGetCrtcTransform, RandrSetCrtcConfig

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...ctx import Ctx
    from .gctx import Ctx as GCtx


@pre
def hasRandr(self, *_a, **_kwa):
    if not self.ctx.gctx.avail('RANDR'):
        raise BaseException('Xrandr is requred for this function')


@pre
def hasDpms(self, *_a, **_kwa):
    if not self.ctx.gctx.avail('DPMS'):
        raise BaseException('X11 DPMS is required for this function')


@applyPre
class Display(GDisplay):
    def __init__(
        self, ctx: 'Ctx[GCtx]', x: int, y: int, width: int, height: int
    ) -> None:
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

    @hasRandr
    async def scale(self, x: float, y: float):
        # https://gitlab.freedesktop.org/xorg/app/xrandr/-/blob/master/xrandr.c?ref_type=heads#L3022
        filter = b'nearest' if round(x) == x and round(y) == y else b'bilinear'

        # https://github.com/winft/disman/blob/fdc697e27f28e45524ec146184ad61ed1de74062/backends/xrandr/xrandroutput.cpp#L459

        transform = await RandrGetCrtcTransform(
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

        await RandrSetCrtcConfig(
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

        transform = await RandrGetCrtcTransform(
            self.ctx, self.ctx.gctx.connection, self._crtc
        ).reply()


@applyPre
class Screen(
    GScreen
):  # idk if wayland has an equivalent for rootDepth, so i wont put it here yet
    def __init__(self, ctx: 'Ctx[GCtx]', screen) -> None:
        self.width: int = screen.widthInPixels
        self.height: int = screen.heightInPixels
        self.root: int = screen.root
        self.screen = screen
        self.ctx = ctx
        self.displays: list[Display] = []

    @hasDpms
    def turnOff(self):
        xcb.xcbDpmsForceLevel(self.ctx.gctx.connection, xcb.XCBDpmsDpmsModeOff)

    @hasDpms
    def turnOn(self):
        xcb.xcbDpmsForceLevel(self.ctx.gctx.connection, xcb.XCBDpmsDpmsModeOn)

    @hasDpms
    def setTimeout(self, t: int):
        # ? should these be seperated
        xcb.xcbDpmsSetTimeouts(self.ctx.gctx.connection, t, t, t)

    @hasDpms
    def disableTimeout(self):
        xcb.xcbDpmsDisable(self.ctx.gctx.connection)

    @hasDpms
    def enableTimeout(self):
        xcb.xcbDpmsEnable(self.ctx.gctx.connection)
