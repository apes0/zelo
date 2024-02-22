import logging
from .keys import Key, Mod
from .mouse import Button
from lib.extension import setupExtensions
from xcb_cffi import ffi, lib
from .types import (
    intp,
    uintarr,
    createNotifyTC,
    mapRequestTC,
    confRequestTC,
    confNotifyTC,
    clientMessageTC,
    destroyNotifyTC,
    unmapNotifyTC,
    motionNotifyTC,
    genericErrorTC,
    buttonPressTC,
    keyPressTC,
    enterNotifyTC,
    mapNotifyTC,
    randrNotifyTC,
    ExposeTC,
)
from lib.cfg import cfg
from .connection import Connection
from typing import TYPE_CHECKING
from .. import events
from .gctx import Ctx as GCtx
from ...watcher import watch

if TYPE_CHECKING:
    from lib.ctx import Ctx
    from lib.backends.generic import GConnection, GWindow

# this is mainly based on this code: https://github.com/mcpcpc/xwm/blob/main/xwm.c

handlers = {}


def handler(n):
    def decorator(fn):
        handlers[n] = fn

    return decorator


@handler(lib.XCB_CREATE_NOTIFY)
async def createNotify(event, ctx: 'Ctx'):
    event = createNotifyTC(event)
    window = ctx.getWindow(event.window)
    ignore = event.override_redirect

    window.ignore = ignore
    #    await window.configure(
    #        newX=max(0, event.x),
    #        newY=max(0, event.y),
    #        newHeight=event.height,
    #        newWidth=event.width,
    #        newBorderWidth=event.border_width,
    #        #        wait=False,
    #    )

    await window.createNotify.trigger(ctx)
    await events.createNotify.trigger(ctx, window)


@handler(lib.XCB_MAP_REQUEST)
async def mapRequest(event, ctx: 'Ctx'):
    # NOTE: its not our responsibility to map or focus the window, the tiler should do so
    event = mapRequestTC(event)
    _id: int = event.window
    window: GWindow = ctx.getWindow(_id)
    window.parent = ctx.getWindow(event.parent)
    ctx.values[0] = lib.XCB_EVENT_MASK_ENTER_WINDOW | lib.XCB_EVENT_MASK_FOCUS_CHANGE
    lib.xcb_change_window_attributes_checked(
        ctx.connection, _id, lib.XCB_CW_EVENT_MASK, ctx.values
    )

    await window.mapRequest.trigger(ctx)
    await events.mapRequest.trigger(ctx, window)


@handler(lib.XCB_CONFIGURE_REQUEST)
async def confRequest(event, ctx: 'Ctx'):
    # TODO: there is a parent field, so should i follow it?
    event = confRequestTC(event)
    window = ctx.getWindow(event.window)
    valueMask = event.value_mask
    change = []
    for mask, (value, lable) in {
        lib.XCB_CONFIG_WINDOW_X: (event.x, 'x'),
        lib.XCB_CONFIG_WINDOW_Y: (event.y, 'y'),
        lib.XCB_CONFIG_WINDOW_WIDTH: (event.width, 'width'),
        lib.XCB_CONFIG_WINDOW_HEIGHT: (event.height, 'height'),
        lib.XCB_CONFIG_WINDOW_BORDER_WIDTH: (event.border_width, 'borderWidth'),
        lib.XCB_CONFIG_WINDOW_SIBLING: (event.sibling, 'sibling'),
        lib.XCB_CONFIG_WINDOW_STACK_MODE: (event.stack_mode, 'stackMode'),
    }.items():
        if mask & valueMask:
            change.append(max(value, 0))  # safety first :)
            window.__dict__[lable] = value

    vals = uintarr(change)
    lib.xcb_configure_window(
        ctx.connection,
        event.window,
        valueMask,
        vals,
    )

    lib.xcb_flush(ctx.connection)

    await window.configureRequest.trigger(ctx)
    await events.configureRequest.trigger(ctx, window)


@handler(lib.XCB_CONFIGURE_NOTIFY)
async def confNotify(event, ctx: 'Ctx'):
    event = confNotifyTC(event)
    window: GWindow = ctx.getWindow(event.window)
    ignore = event.override_redirect
    window.ignore = ignore

    change = {
        event.x: 'x',
        event.y: 'y',
        event.width: 'width',
        event.height: 'height',
        event.border_width: 'borderWdith',
    }
    for val, lable in change.items():
        window.__dict__[lable] = val

    await window.configureNotify.trigger(ctx)
    await events.configureNotify.trigger(ctx, window)


@handler(lib.XCB_CLIENT_MESSAGE)
async def clientMessage(event, ctx: 'Ctx'):
    event = clientMessageTC(event)
    data = event.data
    data = {8: data.data8, 16: data.data16, 32: data.data32}[event.format]


#    print(event.type, [n for n in data])


#    ctx.atomStore.handle(ctx, event.type, data, event.window)


@handler(lib.XCB_DESTROY_NOTIFY)
async def destroyNotify(event, ctx: 'Ctx'):
    event = destroyNotifyTC(event)
    # NOTE: actually doesn't appear to be that slow, check this:
    # https://wiki.python.org/moin/TimeComplexity
    window: int = event.window
    win: GWindow = ctx.getWindow(window)
    win.destroyed = True

    if ctx.focused and window == ctx.focused.id:
        win.mapped = False
        await win.setFocus(False)
        del ctx.windows[window]

    elif (
        window in ctx.windows
    ):  # always returns true for the focused window, thats why its an elif
        win.focused = False
        win.mapped = False
        del ctx.windows[window]
    # NOTE: not our job to select another window to focus to

    await win.destroyNotify.trigger(ctx)
    await events.destroyNotify.trigger(ctx, win)


@handler(lib.XCB_MAP_NOTIFY)
async def mapNotify(event, ctx: 'Ctx'):
    event = mapNotifyTC(event)
    _id = event.window
    win: GWindow = ctx.getWindow(_id)
    ignore = event.override_redirect
    win.ignore = ignore

    await win.mapNotify.trigger(ctx)
    await events.mapNotify.trigger(ctx, win)


@handler(lib.XCB_UNMAP_NOTIFY)
async def unmapNotify(event, ctx: 'Ctx'):
    event = unmapNotifyTC(event)
    _id = event.window
    win: GWindow = ctx.getWindow(_id)

    # NOTE: we shouldn't actually delete here as we can unmap without destroying the window

    if ctx.focused and _id == ctx.focused.id:
        win.mapped = False
        await win.setFocus(False)
    #        del ctx.windows[_id]

    elif (
        _id in ctx.windows
    ):  # always returns true for the focused window, thats why its an elif
        win.mapped = False
        win.focused = False
    #        del ctx.windows[_id]

    await win.unmapNotify.trigger(ctx)
    await events.unmapNotify.trigger(ctx, win)


@handler(lib.XCB_MOTION_NOTIFY)
async def motionNotify(event, ctx: 'Ctx'):
    # TODO: when does this get called???
    event = motionNotifyTC(event)


#    print(
#        event.detail,
#        event.root,
#        event.event,
#        event.child,
#        event.root_x,
#        event.root_y,
#        event.event_x,
#        event.event_y,
#        event.state,
#    )


@handler(0)
async def error(event, ctx: 'Ctx'):
    event = genericErrorTC(event)
    logging.error(
        f'{event.error_code} ({event.major_code}.{event.minor_code}) for resource {event.resource_id}'
    )
    # TODO: xcb-util-errors


@handler(lib.XCB_KEY_PRESS)
async def keyPress(event, ctx: 'Ctx'):
    event = keyPressTC(event)
    key = Key(code=event.detail)
    mod = Mod(value=event.state)
    window: GWindow = ctx.getWindow(event.child)

    await window.keyPress.trigger(ctx, key, mod)
    await events.keyPress.trigger(ctx, key, mod, window)


@handler(lib.XCB_KEY_RELEASE)
async def keyRelease(event, ctx: 'Ctx'):
    event = keyPressTC(event)
    key = Key(code=event.detail)
    mod = Mod(value=event.state)
    window: GWindow = ctx.getWindow(event.event)

    await window.keyRelease.trigger(ctx, key, mod)
    await events.keyRelease.trigger(ctx, key, mod, window)


@handler(lib.XCB_BUTTON_PRESS)
async def buttonPress(event, ctx: 'Ctx'):
    event = buttonPressTC(event)
    button = Button(button=event.detail)
    mod = Mod(value=event.state)
    window: GWindow = ctx.getWindow(event.event)

    await window.buttonPress.trigger(ctx, button, mod)
    await events.buttonPress.trigger(ctx, button, mod, window)


@handler(lib.XCB_BUTTON_RELEASE)
async def buttonRelease(event, ctx: 'Ctx'):
    event = buttonPressTC(event)
    button = Button(button=event.detail)
    mod = Mod(value=event.state)
    window: GWindow = ctx.getWindow(event.event)

    await window.buttonRelease.trigger(ctx, button, mod)
    await events.buttonRelease.trigger(ctx, button, mod, window)


@handler(lib.XCB_ENTER_NOTIFY)
async def enterNotify(event, ctx: 'Ctx'):
    event = enterNotifyTC(event)
    window: GWindow = ctx.getWindow(event.event)

    await window.enterNotify.trigger(ctx)
    await events.enterNotify.trigger(ctx, window)


@handler(lib.XCB_LEAVE_NOTIFY)
async def leaveNotify(event, ctx: 'Ctx'):
    event = enterNotifyTC(event)
    window: GWindow = ctx.getWindow(event.event)

    await window.leaveNotify.trigger(ctx)
    await events.leaveNotify.trigger(ctx, window)


@handler(lib.XCB_RANDR_NOTIFY)
async def randrNotify(event, ctx: 'Ctx'):
    event = randrNotifyTC(event)


#    print(event.response_type, event.subCode)


@handler(lib.XCB_EXPOSE)
async def expose(event, ctx: 'Ctx'):
    event = ExposeTC(event)

    if event.count:
        return

    #    print(event.x, event.y, event.width, event.height, event.window, event.count)
    window = ctx.getWindow(event.window)

    await window.redraw.trigger(ctx)
    await events.redraw.trigger(ctx, window)


ignore = [9, 10, 14, 89]  # list of events to ignore
# 9 - focus in - it just breaks shit, but i *might* need it
# 10 - focus out - same as focus in
# 14 - idk tbh (XCB_NO_EXPOSURE)
# 89 - also dont know, but i think its something to do with randr

# TODO: verify this info (this will forever be here)


async def setup(ctx: 'Ctx'):
    # this is, in practice, the init function for the ctx
    ctx.dname = ffi.NULL
    ctx.screenp = intp(0)
    ctx.gctx = GCtx(ctx)

    conn: GConnection = Connection(
        ctx
    )  # TODO: put this in the ctx and rename the current ``connection``

    ctx.cfg = cfg
    setupExtensions(ctx, cfg.extensions)

    async def _update():
        await update(ctx, conn)

    watch(lib.xcb_get_file_descriptor(ctx.connection), _update)


async def update(ctx: 'Ctx', conn: 'GConnection'):
    # used to be ``not lib.xcb_connection_has_error(ctx.connection) and not ctx.closed``...
    # the fuck was i thinking?
    # i spent a fucking day on debbuging this shit
    if lib.xcb_connection_has_error(ctx.connection) or ctx.closed:
        conn.disconnect()
        return

    while True:
        event = lib.xcb_poll_for_event(ctx.connection)
        if event == ffi.NULL:
            return
        eventType: int = event.response_type & ~0x80
        if handler := handlers.get(eventType, None):
            ctx.nurs.start_soon(handler, event, ctx)
        elif eventType not in ignore:
            logging.warn(f'No handler for: {eventType}')
