import sys
import os

sys.path.append(os.path.dirname((os.path.realpath(__file__))))

from lib.backends.ffi import load
from lib.ctx import Ctx
from lib import watcher
import trio

ctx = Ctx()


async def main():
    async with trio.open_nursery() as nurs:
        ctx.nurs = nurs
        nurs.start_soon(watcher.setup, ctx)
        nurs.start_soon(load('events').setup, ctx)
        # ? maybe init extensions here?


trio.run(main)
