from logging import DEBUG, ERROR, WARN
from typing import TYPE_CHECKING

import trio

from lib.extension import setupExtensions

from ...debcfg import log
from .. import events, xcb
from .connection import Connection
from .gctx import Ctx as GCtx
from .keys import Key, Mod
from .mouse import Button
from .types import (
    ExposeTC,
    PropertyNotifyTC,
    ReparentNotifyTC,
    buttonPressTC,
    charpp,
    confNotifyTC,
    confRequestTC,
    createNotifyTC,
    destroyNotifyTC,
    enterNotifyTC,
    genericErrorTC,
    intp,
    keyPressTC,
    mapNotifyTC,
    mapRequestTC,
    motionNotifyTC,
    randrNotifyTC,
    uintarr,
    unmapNotifyTC,
    xcbErrorContext,
)

if TYPE_CHECKING:
    from lib.backends.generic import GConnection, GWindow
    from lib.ctx import Ctx

    from .atoms import Atom

# TODO: event handlers for extension events?
# TODO: log on 'windows' log as well
# this is mainly based on this code: https://github.com/mcpcpc/xwm/blob/main/xwm.c

handlers = {}


def handler(n):
    def decorator(fn):
        handlers[n] = fn

    return decorator


@handler(xcb.XCBCreateNotify)
async def createNotify(event, ctx: 'Ctx[GCtx]'):
    event = xcb.XcbCreateNotifyEventT(createNotifyTC(event))

    ctx.gctx.atoms[event.window] = {}

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

    await window.createNotify.trigger()

    await ctx.gctx.updateClientsList()


@handler(xcb.XCBMapRequest)
async def mapRequest(event, ctx: 'Ctx[GCtx]'):
    # NOTE: its not our responsibility to map or focus the window, the tiler should do so
    event = xcb.XcbMapRequestEventT(mapRequestTC(event))
    _id: int = event.window
    window: GWindow = ctx.getWindow(_id)
    log('backend', DEBUG, f'{window} requested to be mapped')
    window.parent = ctx.getWindow(event.parent)
    # TODO: this is the only instance of ctx.values in the code, so we should remove it
    # its just a leftover from the initial code and i think i can remove it
    ctx.gctx.values[0] = (
        xcb.XCBEventMaskEnterWindow
        | xcb.XCBEventMaskLeaveWindow
        | xcb.XCBEventMaskPropertyChange
    )
    xcb.xcbChangeWindowAttributesChecked(
        ctx.gctx.connection, _id, xcb.XCBCwEventMask, ctx.gctx.values
    )

    await window.mapRequest.trigger()


@handler(xcb.XCBConfigureRequest)
async def confRequest(event, ctx: 'Ctx[GCtx]'):
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
        ctx.gctx.connection,
        event.window,
        valueMask,
        vals,
    )

    xcb.xcbFlush(ctx.gctx.connection)

    await window.configureRequest.trigger()


@handler(xcb.XCBConfigureNotify)
async def confNotify(event, ctx: 'Ctx[GCtx]'):
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

    await window.configureNotify.trigger()


# @handler(xcb.XCBClientMessage)
# async def clientMessage(event, ctx: 'Ctx[GCtx]'):
#    event = xcb.XcbClientMessageEventT(clientMessageTC(event))
#    data = event.data
#    data = {8: data.data8, 16: data.data16, 32: data.data32}[event.format]


#    print(event.type, [n for n in data])


#    ctx.atomStore.handle(ctx, event.type, data, event.window)


@handler(xcb.XCBDestroyNotify)
async def destroyNotify(event, ctx: 'Ctx[GCtx]'):
    event = xcb.XcbDestroyNotifyEventT(destroyNotifyTC(event))
    # NOTE: actually doesn't appear to be that slow, check this:
    # https://wiki.python.org/moin/TimeComplexity
    window: int = event.window
    win: GWindow = ctx.getWindow(window)

    log('backend', DEBUG, f'{win} got destroyed')

    win.destroyed = True

    if window in ctx.gctx.atoms:
        del ctx.gctx.atoms[window]

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

    await win.destroyNotify.trigger()

    await ctx.gctx.updateClientsList()


@handler(xcb.XCBMapNotify)
async def mapNotify(event, ctx: 'Ctx[GCtx]'):
    event = xcb.XcbMapNotifyEventT(mapNotifyTC(event))
    _id = event.window
    win: GWindow = ctx.getWindow(_id)

    log('backend', DEBUG, f'{win} was mapped')

    ignore = event.overrideRedirect
    win.ignore = bool(ignore)

    await win.mapNotify.trigger()


@handler(xcb.XCBUnmapNotify)
async def unmapNotify(event, ctx: 'Ctx[GCtx]'):
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

    await win.unmapNotify.trigger()


@handler(xcb.XCBMotionNotify)
async def motionNotify(event, ctx: 'Ctx[GCtx]'):
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
async def error(event, ctx: 'Ctx[GCtx]'):
    event = xcb.XcbGenericErrorT(genericErrorTC(event))

    _errCtx = xcbErrorContext()
    xcb.xcbErrorsContextNew(ctx.gctx.connection, _errCtx)
    errCtx = _errCtx[0]
    extension = charpp()

    major = xcb.xcbErrorsGetNameForMajorCode(errCtx, event.majorCode)
    minor = xcb.xcbErrorsGetNameForMinorCode(errCtx, event.majorCode, event.minorCode)
    error = xcb.xcbErrorsGetNameForError(errCtx, event.errorCode, extension)

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
    xcb.xcbErrorsContextFree(errCtx)


@handler(xcb.XCBKeyPress)
async def keyPress(event, ctx: 'Ctx[GCtx]'):
    event = xcb.XcbKeyPressEventT(keyPressTC(event))
    key = Key(code=event.detail)
    mod = Mod(value=event.state)
    window: GWindow = ctx.getWindow(event.child)

    log(['backend', 'keys'], DEBUG, f'{key} with {mod} pressed on {window}')

    await window.keyPress.trigger(key, mod)


@handler(xcb.XCBKeyRelease)
async def keyRelease(event, ctx: 'Ctx[GCtx]'):
    event = xcb.XcbKeyPressEventT(keyPressTC(event))
    key = Key(code=event.detail)
    mod = Mod(value=event.state)
    window: GWindow = ctx.getWindow(event.event)

    log(['backend', 'keys'], DEBUG, f'{key} with {mod} released on {window}')

    await window.keyRelease.trigger(key, mod)


@handler(xcb.XCBButtonPress)
async def buttonPress(event, ctx: 'Ctx[GCtx]'):
    event = xcb.XcbButtonPressEventT(buttonPressTC(event))
    button = Button(button=event.detail)
    mod = Mod(value=event.state)
    window: GWindow = ctx.getWindow(event.event)

    log(['backend', 'buttons'], DEBUG, f'{button} with {mod} pressed on {window}')

    await window.buttonPress.trigger(button, mod)


@handler(xcb.XCBButtonRelease)
async def buttonRelease(event, ctx: 'Ctx[GCtx]'):
    event = xcb.XcbButtonPressEventT(buttonPressTC(event))
    button = Button(button=event.detail)
    mod = Mod(value=event.state)
    window: GWindow = ctx.getWindow(event.event)

    log(['backend', 'buttons'], DEBUG, f'{button} with {mod} released on {window}')

    await window.buttonRelease.trigger(button, mod)


@handler(xcb.XCBEnterNotify)
async def enterNotify(event, ctx: 'Ctx[GCtx]'):
    event = xcb.XcbEnterNotifyEventT(enterNotifyTC(event))
    window: GWindow = ctx.getWindow(event.event)

    log('backend', DEBUG, f'mouse entered {window}')

    await window.enterNotify.trigger()


@handler(xcb.XCBLeaveNotify)
async def leaveNotify(event, ctx: 'Ctx[GCtx]'):
    event = xcb.XcbEnterNotifyEventT(enterNotifyTC(event))
    window: GWindow = ctx.getWindow(event.event)

    log('backend', DEBUG, f'mouse left {window}')

    await window.leaveNotify.trigger()


@handler(xcb.XCBRandrNotify)
async def randrNotify(event, ctx: 'Ctx[GCtx]'):
    event = randrNotifyTC(event)  # TODO: typing


# TODO: impl this shit lol
#    print(event.responseType, event.subCode)


@handler(xcb.XCBReparentNotify)
async def reparentNotify(event, ctx: 'Ctx[GCtx]'):
    ev = xcb.XcbReparentNotifyEventT(ReparentNotifyTC(event))

    win = ctx.getWindow(ev.window)
    parent = ctx.getWindow(ev.parent)

    await win.reparent.trigger(parent)


@handler(xcb.XCBExpose)
async def expose(event, ctx: 'Ctx[GCtx]'):
    event = xcb.XcbExposeEventT(ExposeTC(event))

    if event.count:
        return

    #    print(event.x, event.y, event.width, event.height, event.window, event.count)
    window = ctx.getWindow(event.window)

    log('backend', DEBUG, f'{window} needs to be redrawn')

    await window.redraw.trigger()


@handler(xcb.XCBPropertyNotify)
async def propertyNotify(event, ctx: 'Ctx[GCtx]'):
    event = xcb.XcbPropertyNotifyEventT(PropertyNotifyTC(event))

    log('backend', DEBUG, f'atom {event.atom} of win {event.window} changed')

    winatoms: dict[int, 'Atom'] | None = ctx.gctx.atoms.get(event.window)
    if not winatoms:
        return

    atom = winatoms.get(event.atom)
    if not atom:
        return

    await atom.read()


ignore = [9, 10, 14, 89]  # list of events to ignore
# 9 - focus in - it just breaks shit, but i *might* need it
# 10 - focus out - same as focus in
# 14 - idk tbh (XCB_NO_EXPOSURE)
# 89 - also dont know, but i think its something to do with randr

# TODO: verify this info (this will forever be here)


# TODO: support event 34 (XCB_MAPPING_NOTIFY)
async def setup(ctx: 'Ctx[GCtx]', task_status=trio.TASK_STATUS_IGNORED):
    # this is, in practice, the init function for the ctx
    gctx = GCtx(ctx)
    gctx.dname = ctx.gctxConf.get('display', xcb.NULL)
    gctx.screenp = intp(0)
    ctx.gctx = gctx

    conn: Connection = Connection(
        ctx
    )  # TODO: put this in the ctx and rename the current ``connection``

    await conn.__ainit__()

    await setupExtensions(ctx, ctx.cfg.extensions)

    async def _update():
        await update(ctx, conn)

    ctx.watcher.watch(xcb.xcbGetFileDescriptor(gctx.connection), _update)

    task_status.started()


async def update(ctx: 'Ctx[GCtx]', conn: 'GConnection'):
    if ctx.closed or xcb.xcbConnectionHasError(ctx.gctx.connection):
        conn.disconnect()
        return

    while not ctx.closed:  # we might get closed ig lol
        event = xcb.xcbPollForEvent(ctx.gctx.connection)
        if event == xcb.NULL:
            return

        eventType: int = event.responseType & ~0x80
        if handler := handlers.get(eventType, None):
            ctx.nurs.start_soon(handler, event, ctx)
        elif eventType not in ignore:
            #            print(eventType - gctx.extResps['RANDR'])
            log('others', WARN, f'No handler for: {eventType}')
