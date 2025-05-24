from typing import TYPE_CHECKING

from ...debcfg import log, DEBUG, WARN
from .. import xcb
from ..generic import GConnection, applyPre
from . import requests
from .keys import Mod
from .mouse import Mouse
from .screen import Display, Screen
from .types import chararr, intp, intarr
from .window import Window
from .atoms import Atom, atoms

if TYPE_CHECKING:
    from ...ctx import Ctx
    from .gctx import Ctx as GCtx


initers = []


def init(fn):
    initers.append(fn)


@applyPre
class Connection(GConnection):
    def __init__(self, ctx: 'Ctx') -> None:
        self.ctx = ctx
        gctx: GCtx = ctx._getGCtx()
        self.conn = xcb.xcbConnect(gctx.dname, gctx.screenp)
        gctx.connection = self.conn
        assert not xcb.xcbConnectionHasError(self.conn), 'Xcb connection error'

    async def __ainit__(self):
        for fn in initers:
            await fn(self.ctx)

    def disconnect(self):
        xcb.xcbDisconnect(self.conn)


@init
async def startRequests(ctx: 'Ctx'):
    await ctx.nurs.start(ctx._getGCtx().requestLoop.start)


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
async def extensions(ctx: 'Ctx'):
    gctx: GCtx = ctx._getGCtx()
    reqs = {}
    names = ['RANDR', 'MIT-SHM', 'XTEST', 'RENDER', 'XINERAMA']

    for name in names:
        reqs[name] = requests.QueryExtension(
            ctx, gctx.connection, len(name), chararr(name.encode())
        )

    for name, req in reqs.items():
        rep = await req.reply()

        gctx.extResps[name] = rep
        log('backend', DEBUG, f'{name} is {"not "*(not rep.present)}present')


async def initRandr(ctx: 'Ctx'):
    gctx: GCtx = ctx._getGCtx()
    conn = gctx.connection
    ctx.screen = Screen(xcb.xcbAuxGetScreen(conn, gctx.screenp[0]))
    ctx._root = ctx.screen.root

    screenRes = await requests.GetScreenResources(ctx, conn, ctx._root).reply()

    first = xcb.xcbRandrGetScreenResourcesCrtcs(screenRes)
    reqs = [
        requests.RandrGetCrtcInfo(ctx, conn, first[n], xcb.XCBCurrentTime)
        for n in range(screenRes.numCrtcs)
    ]

    crtcs: list[xcb.XcbRandrGetCrtcInfoReplyT] = [await req.reply() for req in reqs]

    for n, crtc in enumerate(crtcs):
        if crtc == xcb.NULL or (crtc.width + crtc.height) == 0:
            continue

        d = Display(ctx, crtc.x, crtc.y, crtc.width, crtc.height)

        d._crtc = first[n]
        d._mode = crtc.mode
        d._rotation = crtc.rotation
        d._numOutputs = crtc.numOutputs
        d._outputs = xcb.xcbRandrGetCrtcInfoOutputs(crtc)

        ctx.screen.displays.append(d)

    xcb.xcbRandrSelectInput(conn, ctx._root, xcb.XCBRandrNotifyMaskScreenChange)


async def initXinerama(ctx: 'Ctx'):
    gctx: GCtx = ctx._getGCtx()
    conn = gctx.connection
    ctx.screen = Screen(xcb.xcbAuxGetScreen(conn, gctx.screenp[0]))
    ctx._root = ctx.screen.root

    o = await requests.XineramaQueryScreens(ctx, conn).reply()

    # ctx.screen.
    a = xcb.xcbXineramaQueryScreensScreenInfo(o)

    for n in range(o.number):
        info = a[n]
        ctx.screen.displays.append(
            Display(ctx, info.xOrg, info.yOrg, info.width, info.height)
        )

    r = await requests.GetGeometry(ctx, conn, ctx._root).reply()
    ctx.screen.height = r.height
    ctx.screen.width = r.width
    print(ctx.screen)


@init
async def initScreens(ctx: 'Ctx'):
    gctx: GCtx = ctx._getGCtx()
    if gctx.avail('RANDR'):
        await initRandr(ctx)
    elif gctx.avail('XINERAMA'):
        await initXinerama(ctx)
    else:
        log(
            'backend',
            WARN,
            'can\'t get a list of screens, because neither randr or xinerama are present...',
        )


@init
async def loadAtoms(ctx: 'Ctx'):
    for name, (id, type, fmt) in atoms.items():
        if id is not None:
            continue

        rep = await requests.InternAtom(
            ctx,
            ctx._getGCtx().connection,
            0,
            len(name),
            name.encode(),
        ).reply()

        log('backend', DEBUG, f'loaded atom {name} ({rep.atom})')

        atoms[name] = (rep.atom, type, fmt)


@init
async def initWindows(ctx: 'Ctx'):
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
    req = await requests.QueryTree(ctx, conn, ctx._root).reply()
    win = xcb.xcbQueryTreeChildren(req)
    reqs = {
        win[n]: (
            requests.GetWindowAttributes(ctx, conn, win[n]),
            requests.GetGeometry(ctx, conn, win[n]),
        )
        for n in range(req.childrenLen)
    }

    for _id, req in reqs.items():
        attrs = await req[0].reply()
        mapped = attrs.mapState != xcb.XCBMapStateUnmapped

        x, y, height, width, borderWidth = 0, 0, 0, 0, 0

        if mapped:
            geometry = await req[1].reply()
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
async def createClientsAtom(ctx: 'Ctx'):
    ctx.gctx.clients = Atom(ctx, ctx.root, '_NET_CLIENT_LIST')  # type: ignore


@init
async def initMouse(ctx: 'Ctx'):
    ctx.mouse = Mouse(ctx)


@init
async def initModMap(ctx: 'Ctx'):
    gctx: GCtx = ctx._getGCtx()

    rep = await requests.GetModifierMapping(ctx, gctx.connection).reply()

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
async def shm(ctx: 'Ctx'):
    gctx: GCtx = ctx._getGCtx()
    if not gctx.avail('MIT-SHM'):
        return

    rep = await requests.ShmQueryVersion(ctx, gctx.connection).reply()

    gctx.sharedPixmaps = bool(rep.sharedPixmaps)

    log('backend', DEBUG, f'shared pixmaps are {"not "*(not rep.sharedPixmaps)}present')


@init
async def supportingWmCheck(ctx: 'Ctx'):
    w = ctx.createWindow(1, 1, 1, 1, 1)

    await Atom(ctx, ctx.root, '_NET_SUPPORTING_WM_CHECK').set(intp(w.id), 4)
    await Atom(ctx, w, '_NET_SUPPORTING_WM_CHECK').set(intp(w.id), 4)
    await Atom(ctx, w, 'WM_NAME').set(chararr('Zelo'.encode()), 4)
    await Atom(ctx, w, '_NET_WM_NAME').set(chararr('Zelo'.encode()), 4)
