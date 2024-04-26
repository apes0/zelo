import select
from typing import TYPE_CHECKING, Callable

import trio

if TYPE_CHECKING:
    from .ctx import Ctx

watches = {}


def watch(fd: int, fn: Callable):
    watches[fd] = fn


def unwatch(fd: int):
    del watches[fd]


def loop(ctx: 'Ctx'):
    while not ctx.closed:
        try:
            changed, _, _ = select.select(watches.keys(), [], [])
        except OSError:
            return # just ignore the warning for the bad fd lol
        
        for fd in changed:
            trio.from_thread.run(watches[fd])


async def setup(ctx: 'Ctx'):
    # NOTE: i dont wanna run this in another thread but i might have to
    await trio.to_thread.run_sync(loop, ctx)
