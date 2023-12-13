from typing import Callable, TYPE_CHECKING
import traceback

from .generic import GButton, GKey, GMod, GWindow

if TYPE_CHECKING:
    from ..ctx import Ctx

# these are the generic events, which we export, these should be used instead of directly using the
# backend's event, both wayland and x11 should support all of these


async def caller(fn, *args):
    try:
        await fn(*args)
    except:
        # TODO: do something here
        traceback.print_exc()


class Event:
    def __init__(self, *types: type) -> None:
        self.listeners: list[Callable] = []
        self.types = types

    def addListener(self, fn: Callable):
        self.listeners.append(fn)

    def trigger(self, ctx: 'Ctx', *args):
        # check types
        assert len(self.types) == len(
            args
        ), f'There need to be exactly {len(self.types)} arguments for this event, instead of {len(args)}.'
        for n, _type in enumerate(self.types):
            assert issubclass(
                args[n].__class__, _type
            ), f'argument #{n} must be of type {_type}, instead of {type(args[n])}'

        for fn in self.listeners:
            ctx.nurs.start_soon(caller, fn, *args)


# you might be able to tell that all of these appear to be the same as the x11 events, you would be
# right, the original code was xcb only, so, because i dont wanna change anything, i did this

keyPress = Event(GKey, GMod, GWindow)
keyRelease = Event(GKey, GMod, GWindow)
# ? maybe include the x and y coordinates, but idk
buttonPress = Event(GButton, GMod, GWindow)
buttonRelease = Event(GButton, GMod, GWindow)
mapRequest = Event(GWindow)
unmapNotify = Event(GWindow)
destroyNotify = Event(GWindow)
createNotify = Event(GWindow)
configureNotify = Event(GWindow)
configureRequest = Event(GWindow)
enterNotify = Event(GWindow)
leaveNotify = Event(GWindow)
focusChange = Event(GWindow | None, GWindow | None)  # old, new
