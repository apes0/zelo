from .ewmh import AtomStore
from .window import Window
from ...ctx import Ctx
from xcb_cffi import ffi, lib
from .types import intarr
from ..generic import GConnection
from .screen import Screen


class Connection(GConnection):
    def __init__(self, ctx: Ctx) -> None:
        self.conn = lib.xcb_connect(ctx.dname, ctx.screenp)
        ctx.connection = self.conn
        assert not lib.xcb_connection_has_error(self.conn), 'Xcb connection error'
        #        ctx.atomStore = AtomStore(ctx)
        ctx.screen = Screen(lib.xcb_aux_get_screen(ctx.connection, ctx.screenp[0]))
        ctx._root = ctx.screen.root
        ctx.root = Window(0, 0, 0, ctx._root, ctx)
        ctx.values = intarr([0, 0, 0])  # magic values
        ctx.values[0] = (
            lib.XCB_EVENT_MASK_SUBSTRUCTURE_REDIRECT
            | lib.XCB_EVENT_MASK_STRUCTURE_NOTIFY
            | lib.XCB_EVENT_MASK_SUBSTRUCTURE_NOTIFY
            | lib.XCB_EVENT_MASK_PROPERTY_CHANGE
        )

        lib.xcb_change_window_attributes_checked(
            ctx.connection, ctx._root, lib.XCB_CW_EVENT_MASK, ctx.values
        )
        lib.xcb_ungrab_key(
            ctx.connection, lib.XCB_GRAB_ANY, ctx._root, lib.XCB_MOD_MASK_ANY
        )

        # TODO: set supported ewmh's?

        lib.xcb_flush(self.conn)

    def disconnect(self):
        lib.xcb_disconnect(self.conn)
