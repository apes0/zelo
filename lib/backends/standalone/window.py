from ..generic import GWindow, GKey, GButton, GMod, applyPre
from ..events import Event

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.ctx import Ctx
    from .gctx import Ctx as GCtx


@applyPre
class Window(GWindow):
    def __init__(
        self, height: int, width: int, borderWidth: int, _id: int, ctx: 'Ctx'
    ) -> None:
        gctx: GCtx = ctx._getGCtx()
        self.id = gctx.nextId()
        self.height: int = height
        self.width: int = width
        self.borderWidth: int = borderWidth
        self.x: int = 0
        self.y: int = 0
        self.ctx: 'Ctx' = ctx
        self.focused = False
        self.mapped = False
        self.ignore: bool = False
        self.destroyed: bool = False
        self.parent: GWindow | None = None
        self.mine: bool = False

        self.keyPress = Event('keyPress', GKey, GMod)
        self.keyRelease = Event('keyRelease', GKey, GMod)
        self.buttonPress = Event('buttonPress', GButton, GMod)
        self.buttonRelease = Event('buttonRelease', GButton, GMod)
        self.mapRequest = Event('mapRequest')
        self.mapNotify = Event('mapNotify')
        self.unmapNotify = Event('unmapNotify')
        self.destroyNotify = Event('destroyNotify')
        self.createNotify = Event('createNotify')
        self.configureNotify = Event('configureNotify')
        self.configureRequest = Event('configureRequest')
        self.enterNotify = Event('enterNotify')
        self.leaveNotify = Event('leaveNotify')
        self.redraw = Event('redraw')  # exposure notify for x
        self.reparented = Event('reparented', GWindow)  # my parent
        self.ignored = Event('ignored')  # when we are marked as ignored
