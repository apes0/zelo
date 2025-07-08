from typing import TYPE_CHECKING

from ..generic import GWindow, applyPre

if TYPE_CHECKING:
    from lib.ctx import Ctx

    from .gctx import Ctx as GCtx


@applyPre
class Window(GWindow):
    def __init__(
        self, height: int, width: int, borderWidth: int, _id: int, ctx: 'Ctx[GCtx]'
    ) -> None:
        super().__init__(height, width, borderWidth, _id, ctx)
        self.id = ctx.gctx.nextId()
        self.x: int = 0
        self.y: int = 0
        self.focused = False
        self.mapped = False
        self.ignore: bool = False
        self.destroyed: bool = False
        self.parent: GWindow | None = None
        self.mine: bool = False
