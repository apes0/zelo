import traceback
from logging import DEBUG, ERROR
from typing import TYPE_CHECKING, Callable, Iterable, Coroutine
from typing_extensions import Awaitable
import trio

from ..debcfg import log
from collections import deque

if TYPE_CHECKING:
    from ..ctx import Ctx


async def caller(fn, *args, task_status=trio.TASK_STATUS_IGNORED):
    try:
        task_status.started()
        await fn(*args)
    except trio.Cancelled:
        log('evErrors', ERROR, f'{fn} called with {args} got cancelled')
    except:
        # TODO: do something here
        log(
            'evErrors',
            ERROR,
            f'{fn} called with {args} encountered:\n{traceback.format_exc()}',
        )


# this class is just a list with append and pop, however it keeps indecies constant
# NOTE: while this preserves the index, it does not prevserve the order
class ReuseList[T]:
    def __init__(self):
        self.stuff: list[T | None] = []
        self.empty: deque[int] = deque()

    def append(self, v: T) -> int:
        if self.empty:
            n = self.empty.pop()
            self.stuff[n] = v
            return n

        self.stuff.append(v)
        return len(self.stuff) - 1

    def pop(self, n: int) -> None:
        # o = self.stuff[n]
        self.stuff[n] = None
        self.empty.append(n)
        # return o

    def __iter__(self):
        for v in self.stuff:
            if not v:
                continue
            yield v

    # def __getitem__(self, n) -> T:
    #     return self.stuff[n]

    # def __setitem__(self, n, v):
    #     self.stuff[n] = v


type trans = Callable[..., Iterable]


class Event[*T]:
    def __init__(
        self, ctx: 'Ctx', name: str, proxies: dict['Event', trans | None] | None = None
    ) -> None:
        self.listeners: ReuseList[Callable[[*T], Coroutine]] = ReuseList()
        self.proxies: dict[Event, trans | None] = proxies or {}
        self.name = name
        self.ctx = ctx
        self.filters: ReuseList[Callable] = ReuseList()

    def addProxy(self, event: 'Event', trans: trans | None = None):
        # make this event a proxy to another
        self.proxies[event] = trans

    def removeProxy(self, event: 'Event'):
        del self.proxies[event]

    def addFilter(self, filter: Callable[[*T], Awaitable[bool]]):
        return self.filters.append(filter)

    def removeFilter(self, n: int):
        self.filters.pop(n)

    def addListener(self, fn: Callable[[*T], Coroutine]):
        return self.listeners.append(fn)

    def removeListener(self, n: int):
        self.listeners.pop(n)

    async def trigger(self, *args: *T):
        for filter in self.filters:
            if not await filter(*args):
                log(
                    'events',
                    DEBUG,
                    f'filter {filter} of {self.name} blocked {args}',
                )
                return

        log('events', DEBUG, f'triggering {self.name} with {args}')

        for fn in self.listeners:
            await self.ctx.nurs.start(caller, fn, *args)

        for ev, trans in self.proxies.items():
            await ev.trigger(*(args if not trans else trans(*args)))
