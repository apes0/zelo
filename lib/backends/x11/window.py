from functools import partial
from ..generic import GWindow, GKey, GButton, GMod
from xcb_cffi import ffi, lib
import trio
from .types import uintarr
from typing import TYPE_CHECKING, Callable, Coroutine
from ...cfg import cfg
from ..events import (
    Event,
    focusChange,
    unmapNotify,
    mapNotify,
    configureNotify,
    destroyNotify,
)

if TYPE_CHECKING:
    from ...ctx import Ctx
    from ..events import Event


async def runAndWait(ctx: 'Ctx', event: 'Event', check: Callable, fn: Callable):
    if 0:
        # TODO: figure this out aaaaaa
        print(f'waiting')
        ev = trio.Event()

        async def wait(*args):
            if check(*args):
                ev.set()
                return

        event.addListener(wait)

        fn()
        lib.xcb_flush(ctx.connection)

        await ev.wait()

        event.removeListener(wait)
        print(f'finished')
    else:
        fn()
        lib.xcb_flush(ctx.connection)


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
        fn = partial(lib.xcb_map_window, self.ctx.connection, self.id)
        await runAndWait(self.ctx, mapNotify, lambda *args: args[0].id == self.id, fn)

        self.mapped = True

    async def unmap(self):
        fn = partial(lib.xcb_unmap_window, self.ctx.connection, self.id)
        await runAndWait(self.ctx, unmapNotify, lambda *args: args[0].id == self.id, fn)

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
            lib.xcb_set_input_focus(
                self.ctx.connection,
                lib.XCB_INPUT_FOCUS_POINTER_ROOT,  # seemingly fine?
                self.id,
                lib.XCB_CURRENT_TIME,
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
        lib.xcb_change_window_attributes_checked(
            self.ctx.connection, self.id, lib.XCB_CW_BORDER_PIXEL, uintarr([color])
        )

        lib.xcb_flush(self.ctx.connection)

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
            (newX, 'x'): lib.XCB_CONFIG_WINDOW_X,
            (newY, 'y'): lib.XCB_CONFIG_WINDOW_Y,
            (newWidth, 'width'): lib.XCB_CONFIG_WINDOW_WIDTH,
            (newHeight, 'height'): lib.XCB_CONFIG_WINDOW_HEIGHT,
            (newBorderWidth, 'borderWidth'): lib.XCB_CONFIG_WINDOW_BORDER_WIDTH,
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
            lib.xcb_configure_window,
            self.ctx.connection,
            self.id,
            changed,
            vals,
        )

        await runAndWait(
            self.ctx, configureNotify, lambda *args: args[0].id == self.id, fn
        )

    async def close(self):
        fn = partial(lib.xcb_destroy_window, self.ctx.connection, self.id)

        await runAndWait(
            self.ctx, destroyNotify, lambda *args: args[0].id == self.id, fn
        )

    async def kill(self):
        # the nuclear option
        lib.xcb_kill_client(self.ctx.connection, self.id)
        lib.xcb_flush(self.ctx.connection)
