from .ewmh import AtomStore
from .mouse import Mouse
from .window import Window
from ...ctx import Ctx
from xcb_cffi import ffi, lib
from .types import intarr
from ..generic import GConnection
from .screen import Display, Screen


# TODO: clean this up
class Connection(GConnection):
    def __init__(self, ctx: Ctx) -> None:
        self.conn = lib.xcb_connect(ctx.dname, ctx.screenp)
        ctx.connection = self.conn
        assert not lib.xcb_connection_has_error(self.conn), 'Xcb connection error'
        #        ctx.atomStore = AtomStore(ctx)
        ctx.screen = Screen(lib.xcb_aux_get_screen(self.conn, ctx.screenp[0]))
        ctx._root = ctx.screen.root

        screenRes = lib.xcb_randr_get_screen_resources_reply(
            self.conn,
            lib.xcb_randr_get_screen_resources(self.conn, ctx._root),
            ffi.NULL,
        )

        print(screenRes.num_crtcs)

        first = lib.xcb_randr_get_screen_resources_crtcs(screenRes)
        requests = [
            lib.xcb_randr_get_crtc_info(self.conn, first[n], lib.XCB_CURRENT_TIME)
            for n in range(screenRes.num_crtcs)
        ]

        crtcs = [
            lib.xcb_randr_get_crtc_info_reply(self.conn, req, ffi.NULL)
            for req in requests
        ]

        for crtc in crtcs:
            if crtc == ffi.NULL or (crtc.width + crtc.height) == 0:
                continue
            print(crtc.x, crtc.y, crtc.width, crtc.height)
            ctx.screen.displays.append(Display(crtc.x, crtc.y, crtc.width, crtc.height))

        ctx.root = Window(0, 0, 0, ctx._root, ctx)
        ctx.values = intarr([0, 0, 0])  # magic values
        ctx.values[0] = (
            lib.XCB_EVENT_MASK_SUBSTRUCTURE_REDIRECT
            | lib.XCB_EVENT_MASK_STRUCTURE_NOTIFY
            | lib.XCB_EVENT_MASK_SUBSTRUCTURE_NOTIFY
            | lib.XCB_EVENT_MASK_PROPERTY_CHANGE
        )

        lib.xcb_randr_select_input(
            self.conn, ctx._root, lib.XCB_RANDR_NOTIFY_MASK_SCREEN_CHANGE
        )

        lib.xcb_change_window_attributes_checked(
            self.conn, ctx._root, lib.XCB_CW_EVENT_MASK, ctx.values
        )
        lib.xcb_ungrab_key(self.conn, lib.XCB_GRAB_ANY, ctx._root, lib.XCB_MOD_MASK_ANY)

        # TODO: set supported ewmh's?

        ctx.mouse = Mouse(ctx)

        lib.xcb_flush(self.conn)

    def disconnect(self):
        lib.xcb_disconnect(self.conn)
