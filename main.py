from lib.backends.ffi import load
from lib.ctx import Ctx
import trio

ctx = Ctx()

trio.run(load('eventLoop').loop, ctx)
