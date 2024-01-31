from .ewmh import AtomStore
from .mouse import Mouse
from .window import Window
from ...ctx import Ctx
from xcb_cffi import ffi, lib
from .types import intarr
from ..generic import GConnection
from .screen import Display, Screen


# TODO: clean this up
# TODO: export these to every file which these are connected to
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
            ctx.screen.displays.append(Display(crtc.x, crtc.y, crtc.width, crtc.height))

        ctx.root = Window(0, 0, 0, ctx._root, ctx)
        ctx.values = intarr([0, 0, 0])  # magic values
        ctx.values[0] = (
            lib.XCB_EVENT_MASK_SUBSTRUCTURE_REDIRECT
            | lib.XCB_EVENT_MASK_STRUCTURE_NOTIFY
            | lib.XCB_EVENT_MASK_SUBSTRUCTURE_NOTIFY
            | lib.XCB_EVENT_MASK_PROPERTY_CHANGE
            | lib.XCB_EVENT_MASK_EXPOSURE
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

        ctx.mouse.setCursor(
            ctx.root,
            'cursor',
            'left_ptr',
        )  # TODO: export as plugin/config option (still havent decided which one i prefer more, but this is universal from what i understand)

        # TODO: get x, y, border width, width, height here
        req = lib.xcb_query_tree_reply(
            ctx.connection, lib.xcb_query_tree(ctx.connection, ctx._root), ffi.NULL
        )
        win = lib.xcb_query_tree_children(req)
        requests = {
            win[n]: (
                lib.xcb_get_window_attributes(ctx.connection, win[n]),
                lib.xcb_get_geometry(ctx.connection, win[n]),
            )
            for n in range(req.children_len)
        }

        for _id, req in requests.items():
            attrs = lib.xcb_get_window_attributes_reply(
                ctx.connection, req[0], ffi.NULL
            )
            mapped = attrs.map_state != lib.XCB_MAP_STATE_UNMAPPED

            x, y, height, width, borderWidth = 0, 0, 0, 0, 0

            if mapped:
                geometry = lib.xcb_get_geometry_reply(ctx.connection, req[1], ffi.NULL)
                x, y, height, width, borderWidth = (
                    geometry.x,
                    geometry.y,
                    geometry.height,
                    geometry.width,
                    geometry.border_width,
                )

            win = Window(height, width, borderWidth, _id, ctx)
            win.x = x
            win.y = y
            win.mapped = mapped
            win.ignore = attrs.override_redirect
            ctx.windows[_id] = win

        lib.xcb_flush(self.conn)

    def disconnect(self):
        lib.xcb_disconnect(self.conn)
