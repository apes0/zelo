from lib.backends.ffi import load
from lib.ctx import Ctx

ctx = Ctx()

load('eventLoop').loop(ctx)
