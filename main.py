import sys
import os

sys.path.append(os.path.dirname((os.path.realpath(__file__))))

from lib.backends.ffi import load
from lib.ctx import Ctx
from lib import watcher
import trio


async def main():
    ctx = Ctx()
    async with trio.open_nursery() as nurs:
        ctx.nurs = nurs
        nurs.start_soon(watcher.setup, ctx)
        nurs.start_soon(load('events').setup, ctx)
        # ? maybe init extensions here?


if __name__ == '__main__':
    trio.run(main)
