from ..generic import GCtx
from typing import TYPE_CHECKING
from xcb_cffi import ffi, lib
from .types import charpC

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
