import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import traceback
from logging import FATAL

import trio

from lib.backends.ffi import load
from lib.cfg import cfg
from lib.ctx import Ctx
from lib.debcfg import log


async def main():
    ctx = Ctx()
    ctx.cfg = cfg
    try:
        async with trio.open_nursery() as nurs:
            ctx.nurs = nurs
            await nurs.start(load('events').setup, ctx)
            await nurs.start(ctx.watcher.start, ctx)
    except:
        log('errors', FATAL, f'main function encountered {traceback.format_exc()}')
        return
        # ? maybe init extensions here?


if __name__ == '__main__':
    trio.run(main)
