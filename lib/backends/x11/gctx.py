from ..generic import GCtx
from typing import TYPE_CHECKING
from .. import xcb
from .types import charpC, uintarr
from .window import Window

if TYPE_CHECKING:
    from ...ctx import Ctx as Ctxt
    from ..generic import GWindow


class Ctx(GCtx):
    def __init__(self, ctx: 'Ctxt') -> None:
        self.ctx = ctx
        self.extResps = {}

    def avail(self, ext: str):
        return self.extResps[ext].present

    def sendEvent(self, event, window: 'GWindow') -> None:
        xcb.xcbSendEvent(
            self.ctx.connection,
            1,
            window.id,
            xcb.XCBEventMaskKeyPress | xcb.XCBEventMaskKeyRelease,
            charpC(event),
        )
        xcb.xcbFlush(self.ctx.connection)

    def createWindow(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        borderWidth: int,
        parent: Window,
        ignore: bool,
    ):
        window = xcb.xcbGenerateId(self.ctx.connection)
        xcb.xcbCreateWindow(
            self.ctx.connection,
            xcb.XCBCopyFromParent,
            window,
            parent.id,
            x,
            y,
            width,
            height,
            borderWidth,
            xcb.XCBWindowClassInputOutput,
            self.ctx.screen.screen.rootVisual,
            xcb.XCBCwOverrideRedirect | xcb.XCBCwEventMask,  # TODO: maybe set masks idk
            uintarr([ignore, xcb.XCBEventMaskExposure]),
        )

        win = Window(height, width, borderWidth, window, self.ctx)
        # TODO: maybe move these to the args
        win.parent = parent
        win.mine = True

        return win
