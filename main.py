import sys
import os

sys.path.append(os.path.dirname((os.path.realpath(__file__))))

from lib.backends.ffi import load
from lib.ctx import Ctx
from lib.debcfg import log
from lib.cfg import cfg
from logging import FATAL
import traceback
import trio


async def main():
    ctx = Ctx()
    ctx.cfg = cfg
    async with trio.open_nursery() as nurs:
        ctx.nurs = nurs
        try:
            await nurs.start(load('events').setup, ctx)
            await nurs.start(ctx.watcher.start, ctx)
        except:
            log('errors', FATAL, f'main function encountered {traceback.format_exc()}')
            return
        # ? maybe init extensions here?


if __name__ == '__main__':
    trio.run(main)
