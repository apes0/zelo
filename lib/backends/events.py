import traceback
from types import NoneType, UnionType
from typing import TYPE_CHECKING, Callable

import trio

from logging import ERROR, DEBUG
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
        log('evErrors', ERROR, f'{fn} called with {args} encountered:\n{traceback.format_exc()}')


class Event:
    def __init__(self, name: str, *types: type | UnionType) -> None:
        self.listeners: dict['Ctx', list[Callable]] = {}
        self.name = name
        self.types = types
        self.block = False
        # NOTE: i dont like this that much, but it makes the api more reasonable to use

    def addListener(self, ctx: 'Ctx', fn: Callable):
        self.listeners[ctx] = [*self.listeners.get(ctx, []), fn]

    def removeListener(self, ctx: 'Ctx', fn: Callable):
        self.listeners[ctx].remove(fn)
        # TODO: make this faster (prolly will have to use a dictionary)

    async def trigger(self, ctx: 'Ctx', *args):
        if self.block:
            log('events', DEBUG, f'skipping {self.name} with {args} because of block')
            return

        log('events', DEBUG, f'triggering {self.name} with {args}')

        # check types

        assert len(self.types) == len(
            args
        ), f'There need to be exactly {len(self.types)} arguments for event {self.name}, instead of {len(args)}.'

        for n, _type in enumerate(self.types):
            assert issubclass(
                args[n].__class__, _type
            ), f'argument #{n} must be of type {_type}, instead of {type(args[n])} for event {self.name}'

        for fn in self.listeners.get(ctx, []):
            await ctx.nurs.start(caller, fn, *args)


# you might be able to tell that all of these appear to be the same as the x11 events, you would be
# right, the original code was xcb only, so, because i dont wanna change anything, i did this

keyPress = Event('keyPress', GKey, GMod, GWindow)
keyRelease = Event('keyRelease', GKey, GMod, GWindow)
# ? maybe include the x and y coordinates, but idk
buttonPress = Event('buttonPress', GButton, GMod, GWindow)
buttonRelease = Event('buttonRelease', GButton, GMod, GWindow)
mapRequest = Event('mapRequest', GWindow)
mapNotify = Event('mapNotify', GWindow)
unmapNotify = Event('unmapNotify', GWindow)
destroyNotify = Event('destroyNotify', GWindow)
createNotify = Event('createNotify', GWindow)
configureNotify = Event('configureNotify', GWindow)
configureRequest = Event('configureRequest', GWindow)
enterNotify = Event('enterNotify', GWindow)
leaveNotify = Event('leaveNotify', GWindow)
focusChange = Event('focusChange', GWindow | NoneType, GWindow | NoneType)  # old, new
redraw = Event('redraw', GWindow)  # exposure notify for x
reparent = Event('reparent', GWindow, GWindow)  # window and its parent
ignored = Event('ignored', GWindow)  # when a window is marked as ignored
