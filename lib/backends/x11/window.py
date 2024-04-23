from functools import partial
from ..generic import GWindow, GKey, GButton, GMod
from .. import xcb
import trio
from .types import uintarr
from typing import TYPE_CHECKING, Callable, Coroutine
from ...cfg import cfg
from ..events import (
    Event,
    focusChange,
)

if TYPE_CHECKING:
    from ...ctx import Ctx
    from ..events import Event


async def runAndWait(ctx: 'Ctx', events: list['Event'], fn: Callable):
    ev = trio.Event()

    async def wait(*args):
        ev.set()

    for event in events:
        event.addListener(wait)

    fn()
    xcb.xcbFlush(ctx.connection)

    await ev.wait()

    for event in events:
        event.removeListener(wait)


class Window(GWindow):
    def __init__(self, height, width, borderWidth, _id, ctx: 'Ctx') -> None:
        self.height: int = height
        self.width: int = width
        self.borderWidth: int = borderWidth
        self.x: int = 0
        self.y: int = 0
        self.id = _id
        self.ctx: 'Ctx' = ctx
        self.parent: Window | None = None
        self.focused: bool = False
        self.mapped: bool = False
        self.destroyed: bool = False
        self.ignore = True  # set by override redirect (also we assume the worst, so we set it to true)
        self.mine: bool = False

        # events:

        self.keyPress = Event('keyPress', GKey, GMod)
        self.keyRelease = Event('keyRelease', GKey, GMod)
        self.buttonPress = Event('buttonPress', GButton, GMod)
        self.buttonRelease = Event('buttonRelease', GButton, GMod)
        self.mapRequest = Event('mapRequest')
        self.mapNotify = Event('mapNotify')
        self.unmapNotify = Event('unmapNotify')
        self.destroyNotify = Event('destroyNotify')
        self.createNotify = Event('createNotify')
        self.configureNotify = Event('configureNotify')
        self.configureRequest = Event('configureRequest')
        self.enterNotify = Event('enterNotify')
        self.leaveNotify = Event('leaveNotify')
        self.redraw = Event('redraw')  # exposure notify for x

    async def map(self):
        fn = partial(xcb.xcbMapWindow, self.ctx.connection, self.id)
        await runAndWait(self.ctx, [self.mapNotify, self.enterNotify, self.redraw], fn)

        self.mapped = True

    async def unmap(self):
        fn = partial(xcb.xcbUnmapWindow, self.ctx.connection, self.id)
        await runAndWait(
            self.ctx, [self.unmapNotify, self.destroyNotify, self.leaveNotify], fn
        )

        self.mapped = False

    async def setFocus(self, focus: bool):
        # print(
        #    self,
        #    self.ctx.focused,
        #    focus,
        # )
        self.focused = focus
        color: int
        # act is the function to be called *after* everything is done
        # its used so that we dont have any conflicts
        act: Coroutine | None = None

        if focus:
            color = cfg.focusedColor
            xcb.xcbSetInputFocus(
                self.ctx.connection,
                xcb.XCBInputFocusPointerRoot,  # seemingly fine?
                self.id,
                xcb.XCBCurrentTime,
            )

            if not self.ctx.focused:
                # if there is not other window that is focused, we dont have anything to do
                self.ctx.focused = self
                act = focusChange.trigger(self.ctx, None, self)
                # print(f'focus on {self.id}, current: {None} with {color}')

            elif self.ctx.focused.id != self.id:
                # if there is a window that is focused, unfocus it first, then focus our window
                old: GWindow = self.ctx.focused

                async def fn():
                    focusChange.block = True
                    await old.setFocus(False)
                    focusChange.block = False
                    self.ctx.focused = self

                    await focusChange.trigger(self.ctx, old, self)

                act = fn()

                # print(
                #    f'focus on {self.id}, current: {self.ctx.focused.id} with {color}'
                # )

        else:
            color = cfg.unfocusedColor
            # if the id of the focused is our id, and only then, we need to unfocus the window,
            # otherwise, if the ids arent the same, then we are already unfocused
            if self.ctx.focused and self.ctx.focused.id == self.id:
                self.ctx.focused = None
                act = focusChange.trigger(self.ctx, self, None)
                # print(f'unfocus on {self.id} with {color}')

        # ? maybe expose this to a separate function?
        xcb.xcbChangeWindowAttributesChecked(
            self.ctx.connection, self.id, xcb.XCBCwBorderPixel, uintarr([color])
        )

        xcb.xcbFlush(self.ctx.connection)

        if act:
            await act

        # no waiting to do here :)

    async def configure(
        self,
        newX: int | None = None,
        newY: int | None = None,
        newWidth: int | None = None,
        newHeight: int | None = None,
        newBorderWidth: int | None = None,
    ):
        compare = {
            (newX, 'x'): xcb.XCBConfigWindowX,
            (newY, 'y'): xcb.XCBConfigWindowY,
            (newWidth, 'width'): xcb.XCBConfigWindowWidth,
            (newHeight, 'height'): xcb.XCBConfigWindowHeight,
            (newBorderWidth, 'borderWidth'): xcb.XCBConfigWindowBorderWidth,
        }

        vals = []
        changed = 0
        new: int | None
        for (new, currentName), change in compare.items():
            if not new:  # check if it was set as an argument
                continue
            new = max(0, new)  # if its negative, it will not work with ``uint``
            current = self.__dict__[currentName]
            if new != current:
                changed |= change
                vals.append(new)
                self.__dict__[currentName] = new

        vals = uintarr(vals)

        if not changed:
            return  # ? does this break shit - limp bizkit?

        fn = partial(
            xcb.xcbConfigureWindow,
            self.ctx.connection,
            self.id,
            changed,
            vals,
        )

        fn()

    #        await runAndWait(self.ctx, [self.configureNotify], fn)

    async def close(self):
        fn = partial(xcb.xcbDestroyWindow, self.ctx.connection, self.id)

        await runAndWait(self.ctx, [self.destroyNotify, self.leaveNotify], fn)

    async def kill(self):
        # the nuclear option
        xcb.xcbKillClient(self.ctx.connection, self.id)
        xcb.xcbFlush(self.ctx.connection)
