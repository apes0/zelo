from typing import TYPE_CHECKING

import pyglet

from lib.backends.generic import GWindow

from ..generic import GCtx, applyPre
from .cfg import HEIGHT, ROOT

if TYPE_CHECKING:
    from lib.ctx import Ctx as Ctxt


@applyPre
class Ctx(GCtx):
    def __init__(self, ctx: 'Ctxt') -> None:
        self.ctx = ctx
        self.toDraw = []
        self.cid = ROOT

    def createWindow(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        borderWidth: int,
        parent: GWindow,
        ignore: bool,
    ) -> GWindow:
        y = HEIGHT - y
        self.toDraw.append(
            pyglet.shapes.BorderedRectangle(x, y, width, height, borderWidth)
        )

    def nextId(self):
        self.cid += 1
        return self.cid
