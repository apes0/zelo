from lib.extension import Extension
from lib.ffi import ffi, lib as xcb
from lib.ctx import Ctx
from lib.types import (
    intp,
    uintarr,
    keyPressTC,
    createNotifyTC,
    mapRequestTC,
    confRequestTC,
    confNotifyTC,
    clientMessageTC,
    destroyNotifyTC,
    mapNotifyTC,
    unmapNotifyTC,
    motionNotifyTC,
    genericErrorTC
)
from lib.connection import Connection
from lib.cfg import keys, extensions
from lib.window import Window

# this is mainly based on this code: https://github.com/mcpcpc/xwm/blob/main/xwm.c

ctx = Ctx()

ctx.dname = ffi.NULL
ctx.screenp = intp(0)
ctx.shortcuts = keys

conn = Connection(ctx)

extension: Extension
for extension, cfg in extensions.items():
    ctx.extensions.append(extension(ctx, cfg))

handlers = {}


def handler(n):
    def decorator(fn):
        handlers[n] = fn

    return decorator

#TODO: handle errors

@handler(xcb.XCB_KEY_PRESS)
def keyPress(event):
    event = keyPressTC(event)
    key = event.detail
    for idx, _key in enumerate(ctx.keys):
        if key == _key:
            break
        if key < _key:
            ctx.keys.insert(idx, key)
            break
    else:
        ctx.keys.append(key)
    fn = ctx.shortcuts.get((tuple(ctx.keys), event.state))
    if fn:
        fn(ctx)
        ctx.keys = []


@handler(xcb.XCB_KEY_RELEASE)
def keyRelease(event):
    event = keyPressTC(event)
    key = event.detail
    if key in ctx.keys:
        ctx.keys.remove(key)
    else:
        # NOTE: if the key doesn't exist in the list of pressed keys, then it is a modifier, and
        # thus, the keys list should be cleared
        ctx.keys.clear()


@handler(xcb.XCB_CREATE_NOTIFY)
def createNotify(event):
    event = createNotifyTC(event)
    window = ctx.getWindow(event.window)
    window.configure(
        newX=max(0, event.x),
        newY=max(0, event.y),
        newHeight=event.height,
        newWidth=event.width,
        newBorderWidth=event.border_width,
    )


@handler(xcb.XCB_MAP_REQUEST)
def mapRequest(event):
    event = mapRequestTC(event)
    _id: int = event.window
    window: Window = ctx.getWindow(_id)
    xcb.xcb_map_window(ctx.connection, _id)
    ctx.values[0] = xcb.XCB_EVENT_MASK_ENTER_WINDOW | xcb.XCB_EVENT_MASK_FOCUS_CHANGE
    xcb.xcb_change_window_attributes_checked(
        ctx.connection, _id, xcb.XCB_CW_EVENT_MASK, ctx.values
    )
    window.setFocus(True)
    ctx.focused = window


@handler(xcb.XCB_CONFIGURE_REQUEST)
def confRequest(event):
    event = confRequestTC(event)
    window = ctx.getWindow(event.window)
    valueMask = event.value_mask
    change = []
    for mask, (value, lable) in {
        xcb.XCB_CONFIG_WINDOW_X: (event.x, 'x'),
        xcb.XCB_CONFIG_WINDOW_Y: (event.y, 'y'),
        xcb.XCB_CONFIG_WINDOW_WIDTH: (event.width, 'width'),
        xcb.XCB_CONFIG_WINDOW_HEIGHT: (event.height, 'height'),
        xcb.XCB_CONFIG_WINDOW_BORDER_WIDTH: (event.border_width, 'borderWidth'),
        xcb.XCB_CONFIG_WINDOW_SIBLING: (event.sibling, 'sibling'),
        xcb.XCB_CONFIG_WINDOW_STACK_MODE: (event.stack_mode, 'stackMode'),
    }.items():
        if mask & valueMask:
            change.append(max(value, 0)) # safety first :)
            window.__dict__[lable] = value

    vals = uintarr(change)
    xcb.xcb_configure_window(
        ctx.connection,
        event.window,
        valueMask,
        vals,
    )

    xcb.xcb_flush(ctx.connection)


@handler(xcb.XCB_CONFIGURE_NOTIFY)
def confNotify(event):
    event = confNotifyTC(event)
    window: Window = ctx.getWindow(event.window)
    change = {
        event.x: 'x',
        event.y: 'y',
        event.width: 'width',
        event.height: 'height',
        event.border_width: 'borderWdith',
    }
    for val, lable in change.items():
        window.__dict__[lable] = val


@handler(xcb.XCB_CLIENT_MESSAGE)
def clientMessage(event):
    event = clientMessageTC(event)
    data = event.data
    data = {8: data.data8, 16: data.data16, 32: data.data32}[event.format]
    print(event.type, [n for n in data])
    ctx.atomStore.handle(ctx, event.type, data, event.window)


@handler(xcb.XCB_DESTROY_NOTIFY)
def destroyNotify(event):
    event = destroyNotifyTC(event)
    # NOTE: actually doesn't appear to be that slow, check this:
    # https://wiki.python.org/moin/TimeComplexity
    if event.window in ctx.windows:
        del ctx.windows[event.window]
    if ctx.windows:
        # TODO: do better lol
        list(ctx.windows.values())[-1].setFocus(True)


@handler(xcb.XCB_UNMAP_NOTIFY)
def unmapNotify(event):
    event = unmapNotifyTC(event)
    window = ctx.getWindow(event.window)
    if window.id in ctx.windows:
        del ctx.windows[window.id]


@handler(xcb.XCB_MAP_NOTIFY)
def mapNotify(event):
    event = mapNotifyTC(event)
    if event.override_redirect:
        return
    # TODO: call the manager here


@handler(xcb.XCB_MOTION_NOTIFY)
def motionNotify(event):
    # TODO: when does this get called???
    event = motionNotifyTC(event)
    print(
        event.detail,
        event.root,
        event.event,
        event.child,
        event.root_x,
        event.root_y,
        event.event_x,
        event.event_y,
        event.state,
    )


@handler(0)
def error(event):
    event = genericErrorTC(event)
    print(event.error_code)

# @handler(xcb.XCB_FOCUS_IN)
# def focusIn(event):
#     event = focusInTC(event)
#     ctx.getWindow(event.event).setFocus(True)


# @handler(xcb.XCB_FOCUS_OUT)
# def focusOut(event):
#     event = focusInTC(event)
#     ctx.getWindow(event.event).setFocus(False)


ignore = [9, 10]  # list of events to ignore
# 9 - focus in - it just breaks shit, but i *might* need it
# 10 - focus out - same as focus in
# TODO: verify this info (this will forever be here)


while not xcb.xcb_connection_has_error(ctx.connection):
    event = xcb.xcb_wait_for_event(ctx.connection)  # todo: dont skip events
    eventType: int = event.response_type & ~0x80
    for extension in ctx.extensions:
        extension.listeners.get(eventType, lambda _ev: 0)(event)
    if handler := handlers.get(eventType, None):  # type:ignore
        handler(event)
    elif eventType not in ignore:
        print(f'!!! No handler for: {eventType}')

conn.disconnect()
