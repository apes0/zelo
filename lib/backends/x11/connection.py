# from .ewmh import AtomStore
from .mouse import Mouse
from .. import xcb
from typing import TYPE_CHECKING
from ..generic import GConnection
from .window import Window
from .types import intarr
from .screen import Display, Screen
from .keys import Mod, Key

if TYPE_CHECKING:
    from ...ctx import Ctx


initers = []

def init(fn):
    initers.append(fn)

class Connection(GConnection):
    def __init__(self, ctx: 'Ctx') -> None:
        self.conn = xcb.xcbConnect(ctx.dname, ctx.screenp)
        ctx.connection = self.conn
        assert not xcb.xcbConnectionHasError(self.conn), 'Xcb connection error'

        for fn in initers:
            fn(ctx)

    def disconnect(self):
        xcb.xcbDisconnect(self.conn)


@init
def initScreens(ctx: 'Ctx'):
    conn = ctx.connection
    ctx.screen = Screen(xcb.xcbAuxGetScreen(conn, ctx.screenp[0]))
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

    crtcs = [
        xcb.xcbRandrGetCrtcInfoReply(conn, req, xcb.NULL) for req in requests
    ]

    for crtc in crtcs:
        if crtc == xcb.NULL or (crtc.width + crtc.height) == 0:
            continue
        ctx.screen.displays.append(Display(crtc.x, crtc.y, crtc.width, crtc.height))
    
    xcb.xcbRandrSelectInput(
        conn, ctx._root, xcb.XCBRandrNotifyMaskScreenChange
    )

@init
def initWindows(ctx: 'Ctx'):
    conn = ctx.connection

    ctx.root = Window(0, 0, 0, ctx._root, ctx)
    ctx.values = intarr([0, 0, 0])  # magic values
    ctx.values[0] = (
        xcb.XCBEventMaskSubstructureRedirect
        | xcb.XCBEventMaskStructureNotify
        | xcb.XCBEventMaskSubstructureNotify
        | xcb.XCBEventMaskPropertyChange
        | xcb.XCBEventMaskExposure
    )

    xcb.xcbChangeWindowAttributesChecked(
        conn, ctx._root, xcb.XCBCwEventMask, ctx.values
    )
    xcb.xcbUngrabKey(conn, xcb.XCBGrabAny, ctx._root, xcb.XCBModMaskAny)

    # TODO: get x, y, border width, width, height here
    req = xcb.xcbQueryTreeReply(
        conn, xcb.xcbQueryTree(conn, ctx._root), xcb.NULL
    )
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
    rep = xcb.xcbGetModifierMappingReply(
        ctx.connection, xcb.xcbGetModifierMappingUnchecked(ctx.connection), xcb.NULL
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

@init
def initSyms(ctx: 'Ctx'):
    Key.syms = xcb.xcbKeySymbolsAlloc(ctx.connection)