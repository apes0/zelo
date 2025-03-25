from functools import partial
import numpy as np

from ..generic import GWindow, GKey, GButton, GMod, applyPre
from .. import xcb
from xcb_cffi import ffi
import trio
from .types import uintarr, maxUVal
from typing import TYPE_CHECKING, Callable
from ...lock import alock, calock
from ..events import Event, focusChange, reparent, ignored

if TYPE_CHECKING:
    from ...ctx import Ctx
    from ..events import Event
    from .gctx import Ctx as GCtx


async def runAndWait(ctx: 'Ctx', events: list['Event'], fn: Callable):
    ev = trio.Event()

    async def wait(*args):
        ev.set()

    for event in events:
        event.addListener(ctx, wait)

    fn()
    gctx: GCtx = ctx._getGCtx()
    xcb.xcbFlush(gctx.connection)

    await ev.wait()

    for event in events:
        event.removeListener(ctx, wait)


@applyPre
class Window(GWindow):
    def __init__(self, height, width, borderWidth, _id, ctx: 'Ctx') -> None:
        super().__init__(height, width, borderWidth, _id, ctx)
        self.x: int = 0
        self.y: int = 0
        self.parent: Window | None = None
        self.focused: bool = False
        self.mapped: bool = False
        self.destroyed: bool = False
        self._ignore = True  # set by override redirect (also we assume the worst, so we set it to true)
        self.mine: bool = False

    @property  # ? this is the only property, so should i add functions to ignore the win instead?
    def ignore(self):
        return self._ignore

    @ignore.setter
    def ignore(self, val):
        self._ignore = val
        # ? can i perhaps do an async setter?
        self.ctx.nurs.start_soon(ignored.trigger, self.ctx, self)
        self.ctx.nurs.start_soon(self.ignored.trigger, self.ctx)

    async def map(self):
        assert not self.ctx.closed, 'conn is closed'

        gctx: GCtx = self.ctx._getGCtx()

        fn = partial(xcb.xcbMapWindow, gctx.connection, self.id)
        await runAndWait(self.ctx, [self.mapNotify, self.enterNotify, self.redraw], fn)

        self.mapped = True

    async def unmap(self):
        assert not self.ctx.closed, 'conn is closed'

        gctx: GCtx = self.ctx._getGCtx()

        fn = partial(xcb.xcbUnmapWindow, gctx.connection, self.id)
        await runAndWait(
            self.ctx, [self.unmapNotify, self.destroyNotify, self.leaveNotify], fn
        )

        self.mapped = False

    @alock
    async def setFocus(self, focus: bool):
        assert not self.ctx.closed, 'conn is closed'

        gctx: GCtx = self.ctx._getGCtx()

        self.focused = focus
        wid = None

        if focus:
            wid = self.id
            old = self.ctx.focused

            if self.ctx.focused and self.ctx.focused.id != self.id:
                # if there is a window that is focused, mark it as unfocused
                old.focused = False

            self.ctx.focused = self

            await focusChange.trigger(self.ctx, old, self)
        else:
            # if the id of the focused is our id, and only then, we need to unfocus the window,
            # otherwise, if the ids arent the same, then we are already unfocused
            if self.ctx.focused and self.ctx.focused.id == self.id:
                await focusChange.trigger(self.ctx, self, None)
                self.ctx.focused = None
                wid = self.ctx._root

        if not wid:
            return

        xcb.xcbSetInputFocus(
            gctx.connection,
            xcb.XCBInputFocusNone,
            wid,
            xcb.XCBCurrentTime,
        )

        xcb.xcbFlush(gctx.connection)

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

        gctx: GCtx = self.ctx._getGCtx()

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
            gctx.connection,
            self.id,
            changed,
            vals,
        )

        fn()
        xcb.xcbFlush(gctx.connection)

    # TODO: what are we missing here
    #        await runAndWait(self.ctx, [self.configureNotify], fn)

    async def setBorderColor(self, color: int):
        assert not self.ctx.closed, 'conn is closed'

        gctx: GCtx = self.ctx._getGCtx()

        xcb.xcbChangeWindowAttributesChecked(
            gctx.connection, self.id, xcb.XCBCwBorderPixel, uintarr([color])
        )

        xcb.xcbFlush(gctx.connection)

    async def toTop(self):
        assert not self.ctx.closed, 'conn is closed'

        gctx: GCtx = self.ctx._getGCtx()

        xcb.xcbConfigureWindow(
            gctx.connection,
            self.id,
            xcb.XCBConfigWindowStackMode,
            uintarr([xcb.XCBStackModeAbove]),
        )

    async def toBottom(self):
        assert not self.ctx.closed, 'conn is closed'

        gctx: GCtx = self.ctx._getGCtx()

        xcb.xcbConfigureWindow(
            gctx.connection,
            self.id,
            xcb.XCBConfigWindowStackMode,
            uintarr([xcb.XCBStackModeBelow]),
        )

    async def close(self):
        assert not self.ctx.closed, 'conn is closed'

        gctx: GCtx = self.ctx._getGCtx()

        fn = partial(xcb.xcbDestroyWindow, gctx.connection, self.id)

        await runAndWait(self.ctx, [self.destroyNotify, self.leaveNotify], fn)

    async def screenshot(
        self,
        x: int = 0,
        y: int = 0,
        width: int | None = None,
        height: int | None = None,
    ) -> np.ndarray:
        assert not self.ctx.closed, 'conn is closed'

        gctx: GCtx = self.ctx._getGCtx()

        width = width or self.width
        height = height or self.height
        useShm = self.ctx.gctx.avail('MIT-SHM')  # type: ignore

        if useShm:
            shm = xcb.createShm(
                gctx.connection, height * width * 4
            )  # TODO: get the *actual* depth here

            resp = xcb.xcbShmGetImageReply(
                gctx.connection,
                xcb.xcbShmGetImageUnchecked(
                    gctx.connection,
                    self.id,
                    x,
                    y,
                    width,
                    height,
                    maxUVal('int'),
                    xcb.XCBImageFormatZPixmap,
                    shm.id,
                    0,
                ),
                xcb.NULL,
            )

            depth = resp.size // (
                width * height
            )  # TODO: i know you can do this better lol

            out = ffi.buffer(shm.addr, resp.size)
        else:
            resp = xcb.xcbGetImageReply(
                gctx.connection,
                xcb.xcbGetImage(
                    gctx.connection,
                    xcb.XCBImageFormatZPixmap,
                    self.id,
                    x,
                    y,
                    width,
                    height,
                    maxUVal('int'),
                ),
                xcb.NULL,
            )

            dat = xcb.xcbGetImageData(resp)

            depth: int = xcb.xcbGetImageDataLength(resp) // (
                width * height
            )  # TODO: same as above here

            out = ffi.buffer(dat, width * height * depth)

        out: np.ndarray = np.frombuffer(out, np.uint8)
        if useShm:
            out = out.copy()  # if this isnt here, we get a segfault loool
            # i think this happens because numpy tries to reference the, now freed, memory
            # (probably because memcpy-ing before doing anything is slower lol)
            xcb.removeShm(gctx.connection, shm)
        out = out.reshape((height, width, depth))
        return out

    async def reparent(self, parent: 'Window', x: int, y: int):
        assert not self.ctx.closed, 'conn is closed'

        gctx: GCtx = self.ctx._getGCtx()

        fn = partial(xcb.xcbReparentWindow, gctx.connection, self.id, parent.id, x, y)

        await runAndWait(self.ctx, [reparent], fn)

    async def kill(self):
        assert not self.ctx.closed, 'conn is closed'

        gctx: GCtx = self.ctx._getGCtx()

        # the nuclear option
        # ? should we wait for something here lol?
        xcb.xcbKillClient(gctx.connection, self.id)
        xcb.xcbFlush(gctx.connection)
