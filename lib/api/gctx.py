from ..backends.ffi import load
from ..backends.generic import *

loaded = load("gctx")

Ctx: type[GCtx] = loaded.Ctx
# sources:
#lib.backends.standalone.gctx
#lib.backends.x11.gctx
