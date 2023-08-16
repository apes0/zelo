from lib.ewmh import AtomStore
from lib.window import Window
from .ctx import Ctx
from .ffi import ffi, lib as xcb
from .types import intarr


class Connection:
    def __init__(self, ctx: Ctx) -> None:
        self.conn = xcb.xcb_connect(ctx.dname, ctx.screenp)
        ctx.connection = self.conn
        assert not xcb.xcb_connection_has_error(self.conn), 'Xcb connection error'
        ctx.atomStore = AtomStore(ctx)
        ctx.screen = xcb.xcb_aux_get_screen(ctx.connection, ctx.screenp[0])
        ctx._root = ctx.screen.root
        ctx.root = Window(0, 0, 0, ctx._root, ctx)
        ctx.focused = ctx.root
        ctx.values = intarr([0, 0, 0])  # magic values
        ctx.values[0] = (
            xcb.XCB_EVENT_MASK_SUBSTRUCTURE_REDIRECT
            | xcb.XCB_EVENT_MASK_STRUCTURE_NOTIFY
            | xcb.XCB_EVENT_MASK_SUBSTRUCTURE_NOTIFY
            | xcb.XCB_EVENT_MASK_PROPERTY_CHANGE
        )

        xcb.xcb_change_window_attributes_checked(
            ctx.connection, ctx._root, xcb.XCB_CW_EVENT_MASK, ctx.values
        )
        xcb.xcb_ungrab_key(
            ctx.connection, xcb.XCB_GRAB_ANY, ctx._root, xcb.XCB_MOD_MASK_ANY
        )

        # TODO: set supported ewmh's?

        xcb.xcb_flush(self.conn)

    def disconnect(self):
        xcb.xcb_disconnect(self.conn)
