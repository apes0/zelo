# from .ewmh import AtomStore
from .mouse import Mouse
from .. import xcb
from typing import TYPE_CHECKING
from ..generic import GConnection
from .window import Window
from .types import intarr
from .screen import Display, Screen
from .keys import Mod
from .types import chararr
from ...debcfg import log
from logging import DEBUG

if TYPE_CHECKING:
    from ...ctx import Ctx
    from .gctx import Ctx as GCtx


initers = []


def init(fn):
    initers.append(fn)


class Connection(GConnection):
    def __init__(self, ctx: 'Ctx') -> None:
        gctx: GCtx = ctx._getGCtx()
        self.conn = xcb.xcbConnect(gctx.dname, gctx.screenp)
        gctx.connection = self.conn
        assert not xcb.xcbConnectionHasError(self.conn), 'Xcb connection error'

        for fn in initers:
            fn(ctx)

    def disconnect(self):
        xcb.xcbDisconnect(self.conn)


@init
def initScreens(ctx: 'Ctx'):
    gctx: GCtx = ctx._getGCtx()
    conn = gctx.connection
    ctx.screen = Screen(xcb.xcbAuxGetScreen(conn, gctx.screenp[0]))
    ctx._root = ctx.screen.root

    screenRes = xcb.xcbRandrGetScreenResourcesReply(
        conn,
        xcb.xcbRandrGetScreenResources(conn, ctx._root),
        xcb.NULL,
    )

    first = xcb.xcbRandrGetScreenResourcesCrtcs(screenRes)
    requests = [
        xcb.xcbRandrGetCrtcInfo(conn, first[n], xcb.XCBCurrentTime)
        for n in range(screenRes.numCrtcs)
    ]

    crtcs = [xcb.xcbRandrGetCrtcInfoReply(conn, req, xcb.NULL) for req in requests]

    for crtc in crtcs:
        if crtc == xcb.NULL or (crtc.width + crtc.height) == 0:
            continue
        ctx.screen.displays.append(Display(crtc.x, crtc.y, crtc.width, crtc.height))

    xcb.xcbRandrSelectInput(conn, ctx._root, xcb.XCBRandrNotifyMaskScreenChange)


@init
def initWindows(ctx: 'Ctx'):
    gctx: GCtx = ctx._getGCtx()
    conn = gctx.connection

    ctx.root = Window(0, 0, 0, ctx._root, ctx)
    gctx.values = intarr([0, 0, 0])  # magic values
    gctx.values[0] = (
        xcb.XCBEventMaskSubstructureRedirect
        | xcb.XCBEventMaskStructureNotify
        | xcb.XCBEventMaskSubstructureNotify
        | xcb.XCBEventMaskPropertyChange
        | xcb.XCBEventMaskExposure
    )  # TODO: remove this shit lol

    xcb.xcbChangeWindowAttributesChecked(
        conn, ctx._root, xcb.XCBCwEventMask, gctx.values
    )
    xcb.xcbUngrabKey(conn, xcb.XCBGrabAny, ctx._root, xcb.XCBModMaskAny)

    # TODO: get x, y, border width, width, height here
    req = xcb.xcbQueryTreeReply(conn, xcb.xcbQueryTree(conn, ctx._root), xcb.NULL)
    win = xcb.xcbQueryTreeChildren(req)
    requests = {
        win[n]: (
            xcb.xcbGetWindowAttributes(conn, win[n]),
            xcb.xcbGetGeometry(conn, win[n]),
        )
        for n in range(req.childrenLen)
    }

    for _id, req in requests.items():
        attrs = xcb.xcbGetWindowAttributesReply(conn, req[0], xcb.NULL)
        mapped = attrs.mapState != xcb.XCBMapStateUnmapped

        x, y, height, width, borderWidth = 0, 0, 0, 0, 0

        if mapped:
            geometry = xcb.xcbGetGeometryReply(conn, req[1], xcb.NULL)
            x, y, height, width, borderWidth = (
                geometry.x,
                geometry.y,
                geometry.height,
                geometry.width,
                geometry.borderWidth,
            )

        win = Window(height, width, borderWidth, _id, ctx)
        win.x = x
        win.y = y
        win.mapped = mapped
        win.ignore = bool(attrs.overrideRedirect)
        ctx.windows[_id] = win

    xcb.xcbFlush(conn)


@init
def initMouse(ctx: 'Ctx'):
    ctx.mouse = Mouse(ctx)


@init
def initModMap(ctx: 'Ctx'):
    gctx: GCtx = ctx._getGCtx()

    rep = xcb.xcbGetModifierMappingReply(
        gctx.connection, xcb.xcbGetModifierMappingUnchecked(gctx.connection), xcb.NULL
    )

    mappings = xcb.xcbGetModifierMappingKeycodes(rep)

    for mod in range(rep.length):
        for i in range(rep.keycodesPerModifier):
            key = mappings[mod * rep.keycodesPerModifier + i]

            if not key:
                break

            Mod.mappings[1 << mod] = [
                *Mod.mappings.get(mod, []),
                key,
            ]


# list of all extensions i had on my x server (via ``xdpyinfo -display :1 -queryExtensions``):
# BIG-REQUESTS  (opcode: 133)
# Composite  (opcode: 142)
# DAMAGE  (opcode: 143, base event: 91, base error: 152)
# DOUBLE-BUFFER  (opcode: 145, base error: 153)
# DPMS  (opcode: 147)
# DRI2  (opcode: 155, base event: 119)
# DRI3  (opcode: 149)
# GLX  (opcode: 152, base event: 95, base error: 158)
# Generic Event Extension  (opcode: 128)
# MIT-SCREEN-SAVER  (opcode: 144, base event: 92)
# MIT-SHM  (opcode: 130, base event: 65, base error: 128)
# NV-CONTROL  (opcode: 157, base event: 121)
# NV-GLX  (opcode: 156)
# Present  (opcode: 148)
# RANDR  (opcode: 140, base event: 89, base error: 147)
# RECORD  (opcode: 146, base error: 154)
# RENDER  (opcode: 139, base error: 142)
# SECURITY  (opcode: 137, base event: 86, base error: 138)
# SHAPE  (opcode: 129, base event: 64)
# SYNC  (opcode: 134, base event: 83, base error: 134)
# X-Resource  (opcode: 150)
# XC-MISC  (opcode: 136)
# XFIXES  (opcode: 138, base event: 87, base error: 140)
# XFree86-DGA  (opcode: 154, base event: 112, base error: 179)
# XFree86-VidModeExtension  (opcode: 153, base error: 172)
# XINERAMA  (opcode: 141)
# XINERAMA  (opcode: 141)
# XInputExtension  (opcode: 131, base event: 66, base error: 129)
# XKEYBOARD  (opcode: 135, base event: 85, base error: 137)
# XTEST  (opcode: 132)
# XVideo  (opcode: 151, base event: 93, base error: 155)


@init
def extensions(ctx: 'Ctx'):
    gctx: GCtx = ctx._getGCtx()
    reqs = {}
    names = ['RANDR', 'MIT-SHM', 'XTEST', 'RENDER']

    for name in names:
        reqs[name] = xcb.xcbQueryExtensionUnchecked(
            gctx.connection, len(name), chararr(name.encode())
        )

    for name, req in reqs.items():
        rep = xcb.xcbQueryExtensionReply(gctx.connection, req, xcb.NULL)

        gctx.extResps[name] = rep
        log('backend', DEBUG, f'{name} is {"not "*(not rep.present)}present')


@init
def shm(ctx: 'Ctx'):
    gctx: GCtx = ctx._getGCtx()
    if not gctx.avail('MIT-SHM'):
        return

    rep = xcb.xcbShmQueryVersionReply(
        gctx.connection, xcb.xcbShmQueryVersion(gctx.connection), xcb.NULL
    )

    gctx.sharedPixmaps = bool(rep.sharedPixmaps)

    log('backend', DEBUG, f'shared pixmaps are {"not "*(not rep.sharedPixmaps)}present')
