from lib.ffi import ffi, lib as xcb
from lib.ctx import Ctx
from lib.types import (
    intp,
    uintarr,
    buttonPressTC,
    keyPressTC,
    createNotifyTC,
    mapRequestTC,
    confRequestTC,
    confNotifyTC,
    enterNotifyTC,
    focusInTC,
    clientMessageTC,
    destroyNotifyTC,
    mapNotifyTC,
    unmapNotifyTC,
)
from lib.connection import setup
from lib.cfg import keys, createWindow
from lib.window import Window

# this is mainly based on this code: https://github.com/mcpcpc/xwm/blob/main/xwm.c

ctx = Ctx()
ctx.shortcuts = keys

ctx.dname = ffi.NULL
ctx.screenp = intp(0)

setup(ctx)

handlers = {}


def handler(n):
    def decorator(fn):
        handlers[n] = fn

    return decorator


@handler(xcb.XCB_KEY_PRESS)
def keyPress(event):
    event = keyPressTC(event)
    key = event.detail
    print(f'{key} pressed')
    for idx, _key in enumerate(ctx.keys):
        if key == _key:
            break
        elif key < _key:
            ctx.keys.insert(idx, key)
            break
    else:
        ctx.keys.append(key)
    ctx.shortcuts.get((tuple(ctx.keys), event.state), lambda _ctx: 0)(ctx)
    print(ctx.keys)


@handler(xcb.XCB_KEY_RELEASE)
def keyRelease(event):
    event = keyPressTC(event)
    key = event.detail
    print(f'{key} released')
    if key in ctx.keys:  # ?
        ctx.keys.remove(event.detail)


@handler(xcb.XCB_CREATE_NOTIFY)
def createNotify(event):
    event = createNotifyTC(event)
    if event.override_redirect:
        return
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
    if not window.x and not window.y:  # TODO: better check for initialization of window
        createWindow(window, ctx)
    ctx.values[0] = xcb.XCB_EVENT_MASK_ENTER_WINDOW | xcb.XCB_EVENT_MASK_FOCUS_CHANGE
    xcb.xcb_change_window_attributes_checked(
        ctx.connection, _id, xcb.XCB_CW_EVENT_MASK, ctx.values
    )
    window.setFocus(True)
    ctx.focused = window


@handler(xcb.XCB_CONFIGURE_REQUEST)
def confRequest(event):
    event = confRequestTC(event)
    valueMask = event.value_mask
    change = []
    for mask, value in {
        xcb.XCB_CONFIG_WINDOW_X: event.x,
        xcb.XCB_CONFIG_WINDOW_Y: event.y,
        xcb.XCB_CONFIG_WINDOW_WIDTH: event.width,
        xcb.XCB_CONFIG_WINDOW_HEIGHT: event.height,
        xcb.XCB_CONFIG_WINDOW_BORDER_WIDTH: event.border_width,
        xcb.XCB_CONFIG_WINDOW_SIBLING: event.sibling,
        xcb.XCB_CONFIG_WINDOW_STACK_MODE: event.stack_mode,
    }.items():
        if mask & valueMask:
            change.append(value)
    vals = uintarr(change)
    xcb.xcb_configure_window(
        ctx.connection,
        event.window,
        valueMask,
        vals,
    )


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


@handler(xcb.XCB_ENTER_NOTIFY)
def enterNotify(event):
    event = enterNotifyTC(event)
    # TODO: support child windows


@handler(xcb.XCB_CLIENT_MESSAGE)
def clientMessage(event):
    event = clientMessageTC(event)
    data = event.data
    data = {8: data.data8, 16: data.data16, 32: data.data32}[event.format]
    print(event.type, [n for n in data])
    ctx.atomStore.handle(ctx, event.type, data, event.window)
    if False:
        # FIXME: make this work :)
        xcb.xcb_change_property(
            ctx.connection,
            xcb.XCB_PROP_MODE_REPLACE,
            event.window,
        )


@handler(xcb.XCB_DESTROY_NOTIFY)
def destroyNotify(event):
    event = destroyNotifyTC(event)
    # NOTE: actually doesn't appear to be that slow, check this:
    # https://wiki.python.org/moin/TimeComplexity
    if event.window in ctx.windows:
        del ctx.windows[event.window]


@handler(xcb.XCB_UNMAP_NOTIFY)
def unmapNotify(event):
    event = unmapNotifyTC(event)


@handler(xcb.XCB_MAP_NOTIFY)
def mapNotify(event):
    event = mapNotifyTC(event)
    if event.override_redirect:
        return
    # TODO: call the manager here


ignore = [0, 9, 10]  # list of events to ignore
# 0 - probably 0x80?
# 9 - FOCUS_IN, it doesn't tell *us* to do anything with the focus
# 10 - FOCUS_OUT - same as above
# TODO: verify this info


while not xcb.xcb_connection_has_error(ctx.connection):
    event = xcb.xcb_wait_for_event(ctx.connection)
    eventType: int = event.response_type & ~0x80
    if handler := handlers.get(eventType, None):  # type:ignore
        handler(event)
    elif eventType not in ignore:
        print(f'!!! No handler for: {eventType}')

xcb.xcb_disconnect(ctx.connection)

# todo: 34, 19, 22, 9, 10, 7, 34, 161?, 23, 17, 18
