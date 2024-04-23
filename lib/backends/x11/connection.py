# from .ewmh import AtomStore
from .mouse import Mouse
from .window import Window
from ...ctx import Ctx
from .. import xcb
from .types import intarr
from ..generic import GConnection
from .screen import Display, Screen


# TODO: clean this up
# TODO: export these to every file which these are connected to
class Connection(GConnection):
    def __init__(self, ctx: Ctx) -> None:
        self.conn = xcb.xcbConnect(ctx.dname, ctx.screenp)
        ctx.connection = self.conn
        assert not xcb.xcbConnectionHasError(self.conn), 'Xcb connection error'
        #        ctx.atomStore = AtomStore(ctx)
        ctx.screen = Screen(xcb.xcbAuxGetScreen(self.conn, ctx.screenp[0]))
        ctx._root = ctx.screen.root

        screenRes = xcb.xcbRandrGetScreenResourcesReply(
            self.conn,
            xcb.xcbRandrGetScreenResources(self.conn, ctx._root),
            xcb.NULL,
        )

        first = xcb.xcbRandrGetScreenResourcesCrtcs(screenRes)
        requests = [
            xcb.xcbRandrGetCrtcInfo(self.conn, first[n], xcb.XCBCurrentTime)
            for n in range(screenRes.numCrtcs)
        ]

        crtcs = [
            xcb.xcbRandrGetCrtcInfoReply(self.conn, req, xcb.NULL) for req in requests
        ]

        for crtc in crtcs:
            if crtc == xcb.NULL or (crtc.width + crtc.height) == 0:
                continue
            ctx.screen.displays.append(Display(crtc.x, crtc.y, crtc.width, crtc.height))

        ctx.root = Window(0, 0, 0, ctx._root, ctx)
        ctx.values = intarr([0, 0, 0])  # magic values
        ctx.values[0] = (
            xcb.XCBEventMaskSubstructureRedirect
            | xcb.XCBEventMaskStructureNotify
            | xcb.XCBEventMaskSubstructureNotify
            | xcb.XCBEventMaskPropertyChange
            | xcb.XCBEventMaskExposure
        )

        xcb.xcbRandrSelectInput(
            self.conn, ctx._root, xcb.XCBRandrNotifyMaskScreenChange
        )

        xcb.xcbChangeWindowAttributesChecked(
            self.conn, ctx._root, xcb.XCBCwEventMask, ctx.values
        )
        xcb.xcbUngrabKey(self.conn, xcb.XCBGrabAny, ctx._root, xcb.XCBModMaskAny)

        # TODO: set supported ewmh's?

        ctx.mouse = Mouse(ctx)

        # TODO: get x, y, border width, width, height here
        req = xcb.xcbQueryTreeReply(
            ctx.connection, xcb.xcbQueryTree(ctx.connection, ctx._root), xcb.NULL
        )
        win = xcb.xcbQueryTreeChildren(req)
        requests = {
            win[n]: (
                xcb.xcbGetWindowAttributes(ctx.connection, win[n]),
                xcb.xcbGetGeometry(ctx.connection, win[n]),
            )
            for n in range(req.childrenLen)
        }

        for _id, req in requests.items():
            attrs = xcb.xcbGetWindowAttributesReply(ctx.connection, req[0], xcb.NULL)
            mapped = attrs.mapState != xcb.XCBMapStateUnmapped

            x, y, height, width, borderWidth = 0, 0, 0, 0, 0

            if mapped:
                geometry = xcb.xcbGetGeometryReply(ctx.connection, req[1], xcb.NULL)
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

        xcb.xcbFlush(self.conn)

    def disconnect(self):
        xcb.xcbDisconnect(self.conn)
