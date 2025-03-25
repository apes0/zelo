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
        super().__init__(height, width, borderWidth, _id, ctx)
        gctx: GCtx = ctx._getGCtx()
        self.id = gctx.nextId()
        self.x: int = 0
        self.y: int = 0
        self.focused = False
        self.mapped = False
        self.ignore: bool = False
        self.destroyed: bool = False
        self.parent: GWindow | None = None
        self.mine: bool = False
