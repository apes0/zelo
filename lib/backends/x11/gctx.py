from typing import TYPE_CHECKING


from .. import xcb
from ..generic import GCtx, applyPre
from .requests import RequestLoop, QueryTree
from .types import charpC, uintarr
from .window import Window

if TYPE_CHECKING:
    from ...ctx import Ctx as Ctxt
    from ..generic import CData, GWindow
    from .atoms import Atom


@applyPre
class Ctx(GCtx):
    def __init__(self, ctx: 'Ctxt') -> None:
        self.ctx = ctx
        self.connection: CData
        self.dname: CData
        self.screenp: CData
        self.values: CData
        self.extResps = {}
        self.clients: Atom
        self.sharedPixmaps: bool = False
        self.atoms: dict[int, dict[int, Atom]] = {}
        self.requestLoop = RequestLoop(ctx)

    def avail(self, ext: str):
        return self.extResps[ext].present

    def sendEvent(self, event, window: 'GWindow') -> None:
        assert not self.ctx.closed, 'conn is closed'

        xcb.xcbSendEvent(
            self.connection,
            1,
            window.id,
            xcb.XCBEventMaskKeyPress | xcb.XCBEventMaskKeyRelease,
            charpC(event),
        )
        xcb.xcbFlush(self.connection)

    def createWindow(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        borderWidth: int,
        parent: Window,
        ignore: bool,
    ):
        assert not self.ctx.closed, 'conn is closed'

        window = xcb.xcbGenerateId(self.connection)
        xcb.xcbCreateWindow(
            self.connection,
            xcb.XCBCopyFromParent,
            window,
            parent.id,
            x,
            y,
            width,
            height,
            borderWidth,
            xcb.XCBWindowClassInputOutput,
            self.ctx.screen.screen.rootVisual,
            xcb.XCBCwOverrideRedirect | xcb.XCBCwEventMask,  # TODO: maybe set masks idk
            uintarr(
                [
                    ignore,
                    xcb.XCBEventMaskExposure
                    | xcb.XCBEventMaskStructureNotify
                    | xcb.XCBEventMaskExposure
                    | xcb.XCBEventMaskPropertyChange,
                ]
            ),
        )

        win = Window(height, width, borderWidth, window, self.ctx)
        # TODO: maybe move these to the args
        win.parent = parent
        win.mine = True

        return win

    def disconnect(self):
        assert not self.ctx.closed, 'conn is closed'

        xcb.xcbDisconnect(self.connection)
        self.connection = xcb.NULL

    async def updateClientsList(self):
        tree = await QueryTree(self.ctx, self.connection, self.ctx.root.id).reply()
        wins = xcb.xcbQueryTreeChildren(tree)
        await self.clients.set(wins, tree.childrenLen)
