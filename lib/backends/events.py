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
    def __init__(self, name: str) -> None:
        self.listeners: dict['Ctx', list[Callable[[*T], Coroutine]]] = {}
        self.proxies: dict['Ctx', dict[Event, trans | None]] = {}
        self.name = name
        self.filters: dict['Ctx', list[Callable]] = {}

    def addProxy(self, ctx: 'Ctx', event: 'Event', trans: trans | None = None):
        # make this event a proxy to another
        if ctx not in self.proxies:
            self.proxies[ctx] = {}
        self.proxies[ctx][event] = trans

    def removeProxy(self, ctx: 'Ctx', event: 'Event'):
        del self.proxies[ctx][event]

    async def addFilter(self, ctx: 'Ctx', filter: Callable):
        if ctx not in self.filters:
            self.filters[ctx] = []

        self.filters[ctx].append(filter)

    async def removeFilter(self, ctx: 'Ctx', filter: Callable):
        self.filters[ctx].remove(filter)

    def addListener(self, ctx: 'Ctx', fn: Callable[[*T], Coroutine]):
        self.listeners[ctx] = [*self.listeners.get(ctx, []), fn]

    def removeListener(self, ctx: 'Ctx', fn: Callable[[*T], Coroutine]):
        self.listeners[ctx].remove(fn)
        # TODO: make this faster (prolly will have to use a dictionary)

    async def trigger(self, ctx: 'Ctx', *args: *T):
        for filter in self.filters.get(ctx, []):
            if not filter(*args):
                log(
                    'events',
                    DEBUG,
                    f'filter {filter} of {self.name} blocked {args}',
                )
                return

        log('events', DEBUG, f'triggering {self.name} with {args}')

        for fn in self.listeners.get(ctx, []):
            await ctx.nurs.start(caller, fn, *args)

        for ev, trans in self.proxies.get(ctx, {}).items():
            await ev.trigger(ctx, *(args if not trans else trans(*args)))


# you might be able to tell that all of these appear to be the same as the x11 events, you would be
# right, the original code was xcb only, so, because i dont wanna change anything, i did this

keyPress = Event[GKey, GMod, GWindow]('keyPress')
keyRelease = Event[GKey, GMod, GWindow]('keyRelease')
# ? maybe include the x and y coordinates, but idk
buttonPress = Event[GButton, GMod, GWindow]('buttonPress')
buttonRelease = Event[GButton, GMod, GWindow]('buttonRelease')
mapRequest = Event[GWindow]('mapRequest')
mapNotify = Event[GWindow]('mapNotify')
unmapNotify = Event[GWindow]('unmapNotify')
destroyNotify = Event[GWindow]('destroyNotify')
createNotify = Event[GWindow]('createNotify')
configureNotify = Event[GWindow]('configureNotify')
configureRequest = Event[GWindow]('configureRequest')
enterNotify = Event[GWindow]('enterNotify')
leaveNotify = Event[GWindow]('leaveNotify')
focusChange = Event[GWindow | None, GWindow | None]('focusChange')  # old, new
redraw = Event[GWindow]('redraw')  # exposure notify for x
reparent = Event[GWindow, GWindow]('reparent')  # window and its parent
ignored = Event[GWindow]('ignored')  # when a window is marked as ignored
