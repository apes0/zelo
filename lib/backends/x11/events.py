from logging import ERROR, WARN, DEBUG
from ...debcfg import log
from .keys import Key, Mod
from .mouse import Button
from lib.extension import setupExtensions
from .. import xcb
from .types import (
    intp,
    uintarr,
    charpp,
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
    xcbErrorContext,
    ReparentNotifyTC,
)
from .connection import Connection
from typing import TYPE_CHECKING, cast
from .. import events
from .gctx import Ctx as GCtx
import trio

if TYPE_CHECKING:
    from lib.ctx import Ctx
    from lib.backends.generic import GConnection, GWindow

# TODO: event handlers for extension events?
# TODO: log on 'windows' log as well
# this is mainly based on this code: https://github.com/mcpcpc/xwm/blob/main/xwm.c

handlers = {}


def handler(n):
    def decorator(fn):
        handlers[n] = fn

    return decorator


@handler(xcb.XCBCreateNotify)
async def createNotify(event, ctx: 'Ctx'):
    event = xcb.XcbCreateNotifyEventT(createNotifyTC(event))
    window = ctx.getWindow(event.window)
    log('backend', DEBUG, f'{window} was created')
    ignore = bool(event.overrideRedirect)

    window.ignore = ignore
    if not ignore:  # if we follow configureNotify, we should follow this?
        await window.configure(
            newX=max(0, event.x),
            newY=max(0, event.y),
            newHeight=event.height,
            newWidth=event.width,
            newBorderWidth=event.borderWidth,
        )

    await window.createNotify.trigger(ctx)
    await events.createNotify.trigger(ctx, window)


@handler(xcb.XCBMapRequest)
async def mapRequest(event, ctx: 'Ctx'):
    # NOTE: its not our responsibility to map or focus the window, the tiler should do so
    event = xcb.XcbMapRequestEventT(mapRequestTC(event))
    _id: int = event.window
    window: GWindow = ctx.getWindow(_id)
    log('backend', DEBUG, f'{window} requested to be mapped')
    window.parent = ctx.getWindow(event.parent)
    # TODO: this is the only instance of ctx.values in the code, so we should remove it
    # its just a leftover from the initial code and i think i can remove it
    ctx.values[0] = xcb.XCBEventMaskEnterWindow | xcb.XCBEventMaskLeaveWindow
    xcb.xcbChangeWindowAttributesChecked(
        ctx.connection, _id, xcb.XCBCwEventMask, ctx.values
    )

    await window.mapRequest.trigger(ctx)
    await events.mapRequest.trigger(ctx, window)


@handler(xcb.XCBConfigureRequest)
async def confRequest(event, ctx: 'Ctx'):
    # TODO: there is a parent field, so should i follow it?
    event = xcb.XcbConfigureRequestEventT(confRequestTC(event))
    window = ctx.getWindow(event.window)

    log('backend', DEBUG, f'{window} sent a configure request')

    valueMask = event.valueMask
    change = []
    for mask, (value, lable) in {
        xcb.XCBConfigWindowX: (event.x, 'x'),
        xcb.XCBConfigWindowY: (event.y, 'y'),
        xcb.XCBConfigWindowWidth: (event.width, 'width'),
        xcb.XCBConfigWindowHeight: (event.height, 'height'),
        xcb.XCBConfigWindowBorderWidth: (event.borderWidth, 'borderWidth'),
        xcb.XCBConfigWindowSibling: (event.sibling, 'sibling'),
        xcb.XCBConfigWindowStackMode: (event.stackMode, 'stackMode'),
    }.items():
        if mask & valueMask:
            change.append(max(value, 0))  # safety first :)
            window.__dict__[lable] = value

    vals = uintarr(change)
    xcb.xcbConfigureWindow(
        ctx.connection,
        event.window,
        valueMask,
        vals,
    )

    xcb.xcbFlush(ctx.connection)

    await window.configureRequest.trigger(ctx)
    await events.configureRequest.trigger(ctx, window)


@handler(xcb.XCBConfigureNotify)
async def confNotify(event, ctx: 'Ctx'):
    event = xcb.XcbConfigureNotifyEventT(confNotifyTC(event))
    window: GWindow = ctx.getWindow(event.window)

    log('backend', DEBUG, f'{window} sent a configure notify')

    ignore = event.overrideRedirect
    window.ignore = bool(ignore)

    change = {
        event.x: 'x',
        event.y: 'y',
        event.width: 'width',
        event.height: 'height',
        event.borderWidth: 'borderWdith',
    }
    for val, lable in change.items():
        window.__dict__[lable] = val

    await window.configureNotify.trigger(ctx)
    await events.configureNotify.trigger(ctx, window)


# @handler(xcb.XCBClientMessage)
# async def clientMessage(event, ctx: 'Ctx'):
#    event = xcb.XcbClientMessageEventT(clientMessageTC(event))
#    data = event.data
#    data = {8: data.data8, 16: data.data16, 32: data.data32}[event.format]


#    print(event.type, [n for n in data])


#    ctx.atomStore.handle(ctx, event.type, data, event.window)


@handler(xcb.XCBDestroyNotify)
async def destroyNotify(event, ctx: 'Ctx'):
    event = xcb.XcbDestroyNotifyEventT(destroyNotifyTC(event))
    # NOTE: actually doesn't appear to be that slow, check this:
    # https://wiki.python.org/moin/TimeComplexity
    window: int = event.window
    win: GWindow = ctx.getWindow(window)

    log('backend', DEBUG, f'{win} got destroyed')

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


@handler(xcb.XCBMapNotify)
async def mapNotify(event, ctx: 'Ctx'):
    event = xcb.XcbMapNotifyEventT(mapNotifyTC(event))
    _id = event.window
    win: GWindow = ctx.getWindow(_id)

    log('backend', DEBUG, f'{win} was mapped')

    ignore = event.overrideRedirect
    win.ignore = bool(ignore)

    await win.mapNotify.trigger(ctx)
    await events.mapNotify.trigger(ctx, win)


@handler(xcb.XCBUnmapNotify)
async def unmapNotify(event, ctx: 'Ctx'):
    event = xcb.XcbUnmapNotifyEventT(unmapNotifyTC(event))
    _id = event.window
    win: GWindow = ctx.getWindow(_id)

    log('backend', DEBUG, f'{win} got unmapped')

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


@handler(xcb.XCBMotionNotify)
async def motionNotify(event, ctx: 'Ctx'):
    # TODO: when does this get called???
    event = motionNotifyTC(event)


#    print(
#        event.detail,
#        event.root,
#        event.event,
#        event.child,
#        event.rootX,
#        event.rootY,
#        event.eventX,
#        event.eventY,
#        event.state,
#    )


@handler(0)
async def error(event, ctx: 'Ctx'):
    event = xcb.XcbGenericErrorT(genericErrorTC(event))

    _errCtx = xcbErrorContext()
    xcb.xcbErrorsContextNew(ctx.connection, _errCtx)
    errCtx = _errCtx[0]
    extension = charpp()

    major = xcb.xcbErrorsGetNameForMajorCode(errCtx, event.majorCode)
    minor = xcb.xcbErrorsGetNameForMinorCode(errCtx, event.majorCode, event.minorCode)
    error = xcb.xcbErrorsGetNameForError(errCtx, event.errorCode, extension)
    xcb.xcbErrorsContextFree(errCtx)

    def toStr(obj):
        if obj == xcb.NULL:
            return 'NULL'

        out = ''
        i = 0

        while ch := obj[i][0]:
            out += chr(ch)
            i += 1

        return out

    log(
        'errors',
        ERROR,
        f'{toStr(error)}: {toStr(extension[0])}, {toStr(major)}: {toStr(minor)} for resource {event.resourceId}',
    )


@handler(xcb.XCBKeyPress)
async def keyPress(event, ctx: 'Ctx'):
    event = xcb.XcbKeyPressEventT(keyPressTC(event))
    key = Key(code=event.detail)
    mod = Mod(value=event.state)
    window: GWindow = ctx.getWindow(event.child)

    log(['backend', 'keys'], DEBUG, f'{key} with {mod} pressed on {window}')

    await window.keyPress.trigger(ctx, key, mod)
    await events.keyPress.trigger(ctx, key, mod, window)


@handler(xcb.XCBKeyRelease)
async def keyRelease(event, ctx: 'Ctx'):
    event = xcb.XcbKeyPressEventT(keyPressTC(event))
    key = Key(code=event.detail)
    mod = Mod(value=event.state)
    window: GWindow = ctx.getWindow(event.event)

    log(['backend', 'keys'], DEBUG, f'{key} with {mod} released on {window}')

    await window.keyRelease.trigger(ctx, key, mod)
    await events.keyRelease.trigger(ctx, key, mod, window)


@handler(xcb.XCBButtonPress)
async def buttonPress(event, ctx: 'Ctx'):
    event = xcb.XcbButtonPressEventT(buttonPressTC(event))
    button = Button(button=event.detail)
    mod = Mod(value=event.state)
    window: GWindow = ctx.getWindow(event.event)

    log(['backend', 'buttons'], DEBUG, f'{button} with {mod} pressed on {window}')

    await window.buttonPress.trigger(ctx, button, mod)
    await events.buttonPress.trigger(ctx, button, mod, window)


@handler(xcb.XCBButtonRelease)
async def buttonRelease(event, ctx: 'Ctx'):
    event = xcb.XcbButtonPressEventT(buttonPressTC(event))
    button = Button(button=event.detail)
    mod = Mod(value=event.state)
    window: GWindow = ctx.getWindow(event.event)

    log(['backend', 'buttons'], DEBUG, f'{button} with {mod} released on {window}')

    await window.buttonRelease.trigger(ctx, button, mod)
    await events.buttonRelease.trigger(ctx, button, mod, window)


@handler(xcb.XCBEnterNotify)
async def enterNotify(event, ctx: 'Ctx'):
    event = xcb.XcbEnterNotifyEventT(enterNotifyTC(event))
    window: GWindow = ctx.getWindow(event.event)

    log('backend', DEBUG, f'mouse entered {window}')

    await window.enterNotify.trigger(ctx)
    await events.enterNotify.trigger(ctx, window)


@handler(xcb.XCBLeaveNotify)
async def leaveNotify(event, ctx: 'Ctx'):
    event = xcb.XcbEnterNotifyEventT(enterNotifyTC(event))
    window: GWindow = ctx.getWindow(event.event)

    log('backend', DEBUG, f'mouse left {window}')

    await window.leaveNotify.trigger(ctx)
    await events.leaveNotify.trigger(ctx, window)


@handler(xcb.XCBRandrNotify)
async def randrNotify(event, ctx: 'Ctx'):
    event = randrNotifyTC(event)  # TODO: typing


# TODO: impl this shit lol
#    print(event.responseType, event.subCode)


@handler(xcb.XCBReparentNotify)
async def reparentNotify(event, ctx: 'Ctx'):
    ev = xcb.XcbReparentNotifyEventT(ReparentNotifyTC(event))

    win = ctx.getWindow(ev.window)
    parent = ctx.getWindow(ev.parent)

    await win.reparented.trigger(ctx, parent)
    await events.reparent.trigger(ctx, win, parent)


@handler(xcb.XCBExpose)
async def expose(event, ctx: 'Ctx'):
    event = xcb.XcbExposeEventT(ExposeTC(event))

    if event.count:
        return

    #    print(event.x, event.y, event.width, event.height, event.window, event.count)
    window = ctx.getWindow(event.window)

    log('backend', DEBUG, f'{window} needs to be redrawn')

    await window.redraw.trigger(ctx)
    await events.redraw.trigger(ctx, window)


ignore = [9, 10, 14, 89]  # list of events to ignore
# 9 - focus in - it just breaks shit, but i *might* need it
# 10 - focus out - same as focus in
# 14 - idk tbh (XCB_NO_EXPOSURE)
# 89 - also dont know, but i think its something to do with randr

# TODO: verify this info (this will forever be here)


# TODO: support event 34 (XCB_MAPPING_NOTIFY)
async def setup(ctx: 'Ctx', task_status=trio.TASK_STATUS_IGNORED):
    # this is, in practice, the init function for the ctx
    ctx.dname = ctx.dname if hasattr(ctx, 'dname') else xcb.NULL
    ctx.screenp = intp(0)
    ctx.gctx = GCtx(ctx)

    conn: GConnection = Connection(
        ctx
    )  # TODO: put this in the ctx and rename the current ``connection``

    setupExtensions(ctx, ctx.cfg.extensions)

    async def _update():
        await update(ctx, conn)

    ctx.watcher.watch(xcb.xcbGetFileDescriptor(ctx.connection), _update)

    task_status.started()


async def update(ctx: 'Ctx', conn: 'GConnection'):
    if xcb.xcbConnectionHasError(ctx.connection) or ctx.closed:
        conn.disconnect()
        return

    while True:
        event = xcb.xcbPollForEvent(ctx.connection)
        if event == xcb.NULL:
            return
        eventType: int = event.responseType & ~0x80
        if handler := handlers.get(eventType, None):
            ctx.nurs.start_soon(handler, event, ctx)
        elif eventType not in ignore:
#            ctx.gctx = cast(GCtx, ctx.gctx)
#            print(eventType - ctx.gctx.extResps['RANDR'])
            log('others', WARN, f'No handler for: {eventType}')
