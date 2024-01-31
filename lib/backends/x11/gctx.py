from ..generic import GCtx
from typing import TYPE_CHECKING
from xcb_cffi import ffi, lib
from .types import charpC, uintarr
from .window import Window

if TYPE_CHECKING:
    from ...ctx import Ctx as Ctxt
    from ..generic import GWindow


class Ctx(GCtx):
    def __init__(self, ctx: 'Ctxt') -> None:
        self.ctx = ctx

    def sendEvent(self, event, window: 'GWindow') -> None:
        lib.xcb_send_event(
            self.ctx.connection,
            1,
            window.id,
            lib.XCB_EVENT_MASK_KEY_PRESS | lib.XCB_EVENT_MASK_KEY_RELEASE,
            charpC(event),
        )
        lib.xcb_flush(self.ctx.connection)

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
        window = lib.xcb_generate_id(self.ctx.connection)
        lib.xcb_create_window(
            self.ctx.connection,
            lib.XCB_COPY_FROM_PARENT,
            window,
            parent.id,
            x,
            y,
            width,
            height,
            borderWidth,
            lib.XCB_WINDOW_CLASS_INPUT_OUTPUT,
            self.ctx.screen.screen.root_visual,
            lib.XCB_CW_OVERRIDE_REDIRECT
            | lib.XCB_CW_EVENT_MASK,  # TODO: maybe set masks idk
            uintarr([ignore, lib.XCB_EVENT_MASK_EXPOSURE]),
        )

        win = Window(height, width, borderWidth, window, self.ctx)
        win.parent = parent

        return win
