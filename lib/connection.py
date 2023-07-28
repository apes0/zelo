from lib.ewmh import AtomStore
from .ctx import Ctx
from .ffi import ffi, lib as xcb
from .types import intarr


def connect(ctx: Ctx):
    conn = xcb.xcb_connect(ctx.dname, ctx.screenp)
    assert not xcb.xcb_connection_has_error(conn), 'Xcb connection error'
    ctx.connection = conn


def setup(ctx: Ctx):
    connect(ctx)
    ctx.atomStore = AtomStore(ctx)
    ctx.screen = xcb.xcb_aux_get_screen(ctx.connection, ctx.screenp[0])
    ctx.values = intarr([0, 0, 0])  # magic values
    ctx.values[0] = (
        xcb.XCB_EVENT_MASK_SUBSTRUCTURE_REDIRECT
        | xcb.XCB_EVENT_MASK_STRUCTURE_NOTIFY
        | xcb.XCB_EVENT_MASK_SUBSTRUCTURE_NOTIFY
        | xcb.XCB_EVENT_MASK_PROPERTY_CHANGE
    )

    xcb.xcb_change_window_attributes_checked(
        ctx.connection, ctx.screen.root, xcb.XCB_CW_EVENT_MASK, ctx.values
    )
    xcb.xcb_ungrab_key(
        ctx.connection, xcb.XCB_GRAB_ANY, ctx.screen.root, xcb.XCB_MOD_MASK_ANY
    )
    xcb.xcb_flush(ctx.connection)

    # grab mouse buttons
    # mouse = [1, 2, 3]  # 1 - left click, 2 - middle click, 3 - right click

    # for button in mouse:
    #     xcb.xcb_grab_button(
    #         ctx.connection,
    #         0,
    #         ctx.screen.root,
    #         xcb.XCB_EVENT_MASK_BUTTON_PRESS | xcb.XCB_EVENT_MASK_BUTTON_RELEASE,
    #         xcb.XCB_GRAB_MODE_ASYNC,
    #         xcb.XCB_GRAB_MODE_ASYNC,
    #         ctx.screen.root,
    #         xcb.XCB_NONE,
    #         button,
    #         xcb.XCB_MOD_MASK_ANY,
    #     )

    keys = ctx.shortcuts.keys()
    # NOTE: use xcb.XCB_GRAB_ANY for key to find the keycode
    # keys = [xcb.XCB_GRAB_ANY]
    # TODO: ignore caps and numlock
    for key in keys:
        mod = key[1]
        for key in key[0]:
            xcb.xcb_grab_key(
                ctx.connection,
                0,
                ctx.screen.root,
                mod,
                key,
                xcb.XCB_GRAB_MODE_ASYNC,
                xcb.XCB_GRAB_MODE_ASYNC,
            )

    # TODO: set supported ewmh's?

    xcb.xcb_flush(ctx.connection)
