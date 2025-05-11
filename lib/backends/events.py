import traceback
from logging import DEBUG, ERROR
from typing import TYPE_CHECKING, Callable, Iterable, Coroutine
import trio

from ..debcfg import log
from .generic import GButton, GKey, GMod, GWindow

if TYPE_CHECKING:
    from ..ctx import Ctx

# these are the generic events, which we export, these should be used instead of directly using the
# backend's event, both wayland and x11 should support all of these


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


type trans = Callable[..., Iterable]


class Event[*T]:
    def __init__(self, ctx: 'Ctx', name: str) -> None:
        self.listeners: list[Callable[[*T], Coroutine]] = []
        self.proxies: dict[Event, trans | None] = {}
        self.name = name
        self.ctx = ctx
        self.filters: list[Callable] = []

    def addProxy(self, event: 'Event', trans: trans | None = None):
        # make this event a proxy to another
        self.proxies[event] = trans

    def removeProxy(self, event: 'Event'):
        del self.proxies[event]

    def addFilter(self, filter: Callable):
        self.filters.append(filter)

    def removeFilter(self, filter: Callable):
        self.filters.remove(filter)

    def addListener(self, fn: Callable[[*T], Coroutine]):
        self.listeners.append(fn)

    def removeListener(self, fn: Callable[[*T], Coroutine]):
        self.listeners.remove(fn)

    async def trigger(self, *args: *T):
        for filter in self.filters:
            if not filter(*args):
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
