import select
from typing import Callable, TYPE_CHECKING
import trio

if TYPE_CHECKING:
    from .ctx import Ctx

watches = {}


def watch(fd: int, fn: Callable):
    watches[fd] = fn


def unwatch(fd: int):
    del watches[fd]


def loop():
    while True:
        changed, _, _ = select.select(watches.keys(), [], [])
        for fd in changed:
            trio.from_thread.run(watches[fd])


async def setup(ctx: 'Ctx'):
    # NOTE: i dont wanna run this in another thread but i might have to
    await trio.to_thread.run_sync(loop)
