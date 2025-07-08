from functools import partial
from typing import TYPE_CHECKING
from collections.abc import Callable

import numpy as np
import trio

from lib.backends.x11 import requests
from lib.backends.x11.atoms import Atom
from xcb_cffi import ffi

from ...lock import alock, calock
from .. import xcb
from ..generic import GWindow, applyPre
from .types import maxUVal, uintarr

if TYPE_CHECKING:
    from ...ctx import Ctx
    from ..events import Event
    from .gctx import Ctx as GCtx


async def runAndWait(ctx: 'Ctx[GCtx]', events: list['Event'], fn: Callable):
    ev = trio.Event()
    l = {}

    async def wait(*args):
        ev.set()

    for event in events:
        l[event] = event.addListener(wait)

    fn()
    xcb.xcbFlush(ctx.gctx.connection)

    await ev.wait()

    for e, n in l.items():
        e.removeListener(n)


@applyPre
class Window(GWindow):
    def __init__(self, height, width, borderWidth, _id, ctx: 'Ctx[GCtx]') -> None:
        super().__init__(height, width, borderWidth, _id, ctx)
        self.x: int = 0
        self.y: int = 0
        self.parent: Window | None = None
        self.focused: bool = False
        self.mapped: bool = False
        self.destroyed: bool = False
        self._ignore = True  # set by override redirect (also we assume the worst, so we set it to true)
        self.mine: bool = False
        self._title = Atom(ctx, self, 'WM_NAME')
        self._iconTitle = Atom(ctx, self, 'WM_ICON_NAME')
        self._icon = Atom(ctx, self, '_NET_WM_ICON')
        self._hints = Atom(ctx, self, 'WM_HINTS')
        self._class = Atom(ctx, self, 'WM_CLASS')
        # TODO: export hints somewhere

        # custom events:

        self.titleChanged = self._title.changed
        self.iconTitleChanged = self._iconTitle.changed
        self.iconChanged = self._icon.changed

    async def names(self):
        return await self._class.get()

    async def title(self):
        return (await self._title.get())[0]

    async def iconTitle(self):
        return (await self._iconTitle.get())[0]

    async def icon(self):
        # ? should we prefer the hints icon or the _NET_WM_ICON icon?
        h = await self._hints.get()
        if h and h.icon.any():
            return h.icon
        return await self._icon.get()

    async def state(self):
        return await self._state.get()

    @property  # ? this is the only property, so should i add functions to ignore the win instead?
    def ignore(self):
        return self._ignore

    @ignore.setter
    def ignore(self, val):
        self._ignore = val
        # ? can i perhaps do an async setter?
        self.ctx.nurs.start_soon(self.ignored.trigger)

    async def map(self):
        assert not self.ctx.closed, 'conn is closed'

        fn = partial(xcb.xcbMapWindow, self.ctx.gctx.connection, self.id)
        fn()
        # await runAndWait(self.ctx, [self.mapNotify], fn)

        self.mapped = True

    async def unmap(self):
        assert not self.ctx.closed, 'conn is closed'

        fn = partial(xcb.xcbUnmapWindow, self.ctx.gctx.connection, self.id)
        fn()
        # await runAndWait(self.ctx, [self.unmapNotify], fn)

        self.mapped = False

    @alock
    async def setFocus(self, focus: bool):
        assert not self.ctx.closed, 'conn is closed'

        self.focused = focus
        wid = None

        if focus:
            wid = self.id
            old = self.ctx.focused

            if self.ctx.focused and self.ctx.focused.id != self.id:
                # if there is a window that is focused, mark it as unfocused
                old.focused = False

            self.ctx.focused = self

            await self.ctx.focusChange.trigger(old, self)
        else:
            # if the id of the focused is our id, and only then, we need to unfocus the window,
            # otherwise, if the ids arent the same, then we are already unfocused
            if self.ctx.focused and self.ctx.focused.id == self.id:
                await self.ctx.focusChange.trigger(self, None)
                self.ctx.focused = None
                wid = self.ctx._root

        if not wid:
            return

        xcb.xcbSetInputFocus(
            self.ctx.gctx.connection,
            xcb.XCBInputFocusNone,
            wid,
            xcb.XCBCurrentTime,
        )

        xcb.xcbFlush(self.ctx.gctx.connection)

        # no waiting to do here :)
        # ? should we wait for focusin/out??

    @calock
    async def configure(
        self,
        newX: int | None = None,
        newY: int | None = None,
        newWidth: int | None = None,
        newHeight: int | None = None,
        newBorderWidth: int | None = None,
        #        newStackMode: int | None = None # TODO: should we have this?
    ):
        assert not self.ctx.closed, 'conn is closed'

        compare = {
            (newX, 'x'): xcb.XCBConfigWindowX,
            (newY, 'y'): xcb.XCBConfigWindowY,
            (newWidth, 'width'): xcb.XCBConfigWindowWidth,
            (newHeight, 'height'): xcb.XCBConfigWindowHeight,
            (newBorderWidth, 'borderWidth'): xcb.XCBConfigWindowBorderWidth,
            #            (newSibling, 'sibling'): xcb.XCBConfigWindowSibling, # TODO: what and how
            #            (newStackMode, 'stackMode'): xcb.XCBConfigWindowStackMode,
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
            self.ctx.gctx.connection,
            self.id,
            changed,
            vals,
        )

        fn()
        xcb.xcbFlush(self.ctx.gctx.connection)

        # TODO: what are we missing here
        # await runAndWait(self.ctx, [self.configureNotify], fn)

    async def setBorderColor(self, color: int):
        assert not self.ctx.closed, 'conn is closed'

        xcb.xcbChangeWindowAttributesChecked(
            self.ctx.gctx.connection, self.id, xcb.XCBCwBorderPixel, uintarr([color])
        )

        xcb.xcbFlush(self.ctx.gctx.connection)

    async def toTop(self):
        assert not self.ctx.closed, 'conn is closed'

        xcb.xcbConfigureWindow(
            self.ctx.gctx.connection,
            self.id,
            xcb.XCBConfigWindowStackMode,
            uintarr([xcb.XCBStackModeAbove]),
        )

    async def toBottom(self):
        assert not self.ctx.closed, 'conn is closed'

        xcb.xcbConfigureWindow(
            self.ctx.gctx.connection,
            self.id,
            xcb.XCBConfigWindowStackMode,
            uintarr([xcb.XCBStackModeBelow]),
        )

    async def close(self):
        assert not self.ctx.closed, 'conn is closed'

        fn = partial(xcb.xcbDestroyWindow, self.ctx.gctx.connection, self.id)

        await runAndWait(self.ctx, [self.destroyNotify, self.leaveNotify], fn)

    async def screenshot(
        self,
        x: int = 0,
        y: int = 0,
        width: int | None = None,
        height: int | None = None,
    ) -> np.ndarray:
        assert not self.ctx.closed, 'conn is closed'

        width = width or self.width
        height = height or self.height
        useShm = self.ctx.gctx.avail('MIT-SHM')  # type: ignore

        if useShm:
            shm = xcb.createShm(
                self.ctx.gctx.connection, height * width * 4
            )  # TODO: get the *actual* depth here

            resp = await requests.ShmGetImage(
                self.ctx,
                self.ctx.gctx.connection,
                self.id,
                x,
                y,
                width,
                height,
                maxUVal('int'),
                xcb.XCBImageFormatZPixmap,
                shm.id,
                0,
            ).reply()

            depth = resp.size // (
                width * height
            )  # TODO: i know you can do this better lol

            out = ffi.buffer(shm.addr, resp.size)
        else:
            resp = await requests.GetImage(
                self.ctx,
                self.ctx.gctx.connection,
                xcb.XCBImageFormatZPixmap,
                self.id,
                x,
                y,
                width,
                height,
                maxUVal('int'),
            ).reply()

            dat = xcb.xcbGetImageData(resp)

            depth: int = xcb.xcbGetImageDataLength(resp) // (
                width * height
            )  # TODO: same as above here

            out = ffi.buffer(dat.obj, width * height * depth)

        out: np.ndarray = np.frombuffer(out, np.uint8)
        if useShm:
            out = out.copy()  # if this isnt here, we get a segfault loool
            # i think this happens because numpy tries to reference the, now freed, memory
            # (probably because memcpy-ing before doing anything is slower lol)
            xcb.removeShm(self.ctx.gctx.connection, shm)
        out = out.reshape((height, width, depth))
        return out

    async def reparent(self, parent: 'Window', x: int, y: int):
        assert not self.ctx.closed, 'conn is closed'

        fn = partial(
            xcb.xcbReparentWindow, self.ctx.gctx.connection, self.id, parent.id, x, y
        )

        await runAndWait(self.ctx, [self.ctx.reparent], fn)

    async def kill(self):
        assert not self.ctx.closed, 'conn is closed'

        # the nuclear option
        # ? should we wait for something here lol?
        xcb.xcbKillClient(self.ctx.gctx.connection, self.id)
        xcb.xcbFlush(self.ctx.gctx.connection)
