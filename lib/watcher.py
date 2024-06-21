import select
from typing import TYPE_CHECKING, Callable
from logging import FATAL, DEBUG

import trio

from .debcfg import log

if TYPE_CHECKING:
    from .ctx import Ctx


class Watcher:
    def __init__(self, ctx: 'Ctx') -> None:
        self.watches = {}

    def watch(self, fd: int, fn: Callable):
        log('backend', DEBUG, f'fd {fd} is now being watched (fn = {fn})')
        self.watches[fd] = fn

    def unwatch(self, fd: int):
        log('backend', DEBUG, f'fd {fd} has stopped being watched')
        del self.watches[fd]

    def loop(self, ctx: 'Ctx', finito: Callable):
        trio.from_thread.run_sync(finito)  # task_status.started
        while self.watches:
            try:
                changed, _, _ = select.select(self.watches.keys(), [], [])
            except OSError as e:
                log('errors', FATAL, f'watcher loop encountered {e}')
                return  # just give up and die

            if ctx.closed:
                return

            for fd in changed:
                trio.from_thread.run(self.watches[fd])

    async def start(self, ctx: 'Ctx', task_status: trio._core._run._TaskStatus):
        # NOTE: i dont wanna run this in another thread but i might have to
        await trio.to_thread.run_sync(self.loop, ctx, task_status.started)
