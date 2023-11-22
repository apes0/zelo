from ..backends.ffi import load
from ..backends.generic import *

loaded = load("gctx")

Ctx: type[GCtx] = loaded.Ctx
