from html import escape
from typing import TYPE_CHECKING

import cv2
import numpy as np

from xcb_cffi import ffi

from .. import xcb
from ..generic import GImage, GRectangle, GText, GWindow, applyPre
from ..pango import render
from .types import chararr, rectangle, uchararr, uintarr

if TYPE_CHECKING:
    from ...ctx import Ctx
    from .gctx import Ctx as GCtx
    from .window import Window

# Create gcontext and such here
# do text rendering, image drawing, etc.


@applyPre
class Image(GImage):

    def __init__(
        self,
        ctx: 'Ctx[GCtx]',
        window: 'Window',
        img: np.ndarray | None,
        width: int,
        height: int,
        x: int,
        y: int,
    ) -> None:
        assert not ctx.closed, 'conn is closed'
        self.x: int = x
        self.y: int = y

        self.ctx = ctx

        self.windowId = window.id

        self.width = width
        self.height = height

        self.gc = xcb.xcbGenerateId(ctx.gctx.connection)
        self.pixmap = xcb.xcbGenerateId(ctx.gctx.connection)

        self.image: xcb.XcbImageT
        self.useShm = ctx.gctx.avail('MIT-SHM')

        if self.useShm:
            self.shm = xcb.createShm(ctx.gctx.connection, self.width * self.height * 4)
            if ctx.gctx.sharedPixmaps:
                xcb.xcbShmCreatePixmap(
                    ctx.gctx.connection,
                    self.pixmap,
                    self.windowId,
                    self.width,
                    self.height,
                    ctx.screen.screen.rootDepth,
                    self.shm.id,
                    0,
                )
            else:
                self.pixmap = self.windowId
        else:
            xcb.xcbCreatePixmap(
                ctx.gctx.connection,
                ctx.screen.screen.rootDepth,
                self.pixmap,
                self.windowId,
                self.width,
                self.height,
            )

        xcb.xcbCreateGc(ctx.gctx.connection, self.gc, self.pixmap, 0, xcb.NULL)

        if img is not None:
            self.set(img)

    @classmethod
    def _fromPixmap(cls):
        self: Image = cls.__new__(cls)
        return self

    def set(self, img):
        assert not self.ctx.closed, 'conn is closed'

        img = cv2.resize(img, (self.width, self.height))

        _, _, px = img.shape

        if px == 3:
            img = np.dstack(
                (img, np.ones((self.height, self.width, 1), dtype=np.uint8) * 255)
            )

        if self.useShm:
            data = img.tobytes()
            ffi.memmove(self.shm.addr, data, len(data))
            if not self.ctx.gctx.sharedPixmaps:  # type: ignore
                xcb.xcbShmPutImage(  # TODO: do i need to do this every time, or only once?
                    self.ctx.gctx.connection,
                    self.windowId,
                    self.gc,
                    self.width,
                    self.height,
                    0,
                    0,
                    self.width,
                    self.height,
                    self.x,
                    self.y,
                    self.ctx.screen.screen.rootDepth,
                    xcb.XCBImageFormatZPixmap,
                    0,
                    self.shm.id,
                    0,
                )

        else:
            parts = (self.width * self.height * 4) // xcb.xcbGetMaximumRequestLength(
                self.ctx.gctx.connection
            ) + 2
            # this works with +2 for some reason
            pos = 0
            prev = 0
            size = self.height / parts

            for _ in range(parts):
                # TODO: use the.scanlinePad stuff
                pos += size
                self.image = xcb.xcbImageCreateNative(
                    self.ctx.gctx.connection,
                    self.width,
                    round(pos) - round(prev),
                    xcb.XCBImageFormatZPixmap,
                    self.ctx.screen.screen.rootDepth,
                    xcb.NULL,
                    self.width * (round(pos) - round(prev)) * 4,
                    uchararr(img[round(prev) : round(pos), :, :].tobytes()),
                )

                xcb.xcbImagePut(
                    self.ctx.gctx.connection,
                    self.pixmap,
                    self.gc,
                    self.image,
                    0,
                    round(prev),
                    0,
                )

                prev = pos

        xcb.xcbFlush(self.ctx.gctx.connection)

    def draw(self):
        assert not self.ctx.closed, 'conn is closed'

        if self.useShm and not self.ctx.gctx.sharedPixmaps:  # type: ignore
            xcb.xcbShmPutImage(
                self.ctx.gctx.connection,
                self.windowId,
                self.gc,
                self.width,
                self.height,
                0,
                0,
                self.width,
                self.height,
                self.x,
                self.y,
                self.ctx.screen.screen.rootDepth,
                xcb.XCBImageFormatZPixmap,
                0,
                self.shm.id,
                0,
            )
            return
        xcb.xcbCopyArea(
            self.ctx.gctx.connection,
            self.pixmap,
            self.windowId,
            self.gc,
            0,
            0,
            self.x,
            self.y,
            self.width,
            self.height,
        )

        xcb.xcbFlush(self.ctx.gctx.connection)

    def destroy(self):
        assert not self.ctx.closed, 'conn is closed'

        if self.useShm:
            xcb.removeShm(self.ctx.gctx.connection, self.shm)
        else:
            xcb.xcbImageDestroy(self.image)

        xcb.xcbFreePixmap(self.ctx.gctx.connection, self.pixmap)
        self.pixmap = xcb.NULL
        xcb.xcbFlush(self.ctx.gctx.connection)

    def move(self, x: int, y: int):
        self.x = x
        self.y = y


@applyPre
class Text(GText):

    def __init__(
        self,
        ctx: 'Ctx[GCtx]',
        win: 'Window',
        x: int,
        y: int,
        text: str | None,
        font: str,
        fore: int = 0xFFFFFF,
        back: int = 0x000000,
    ) -> None:
        # TODO: support picture for background as well
        self.text: str = ''
        self.image: Image | None = None
        self.font: str = font
        self.back = back
        self.fore = fore
        self.width: int = -1
        self.height: int = -1
        self.x = x
        self.y = y
        self.win = win
        self.ctx = ctx
        # NOTE: we have to keep this in case we need to resize the text image

        if text:
            self.text = text
            self.set(text)

    def render(self) -> tuple[np.ndarray, int, int]:
        # ? is it a good idea to use xcb's ffi here?
        rendered = render(
            chararr(escape(self.text).encode()),
            chararr(self.font.encode()),
            self.fore,
            self.back,
        )
        out = ffi.buffer(rendered.buffer, rendered.width * rendered.rows * 4)
        out: np.ndarray = np.frombuffer(out, np.uint8)
        out = out.reshape((rendered.rows, rendered.width, 4))

        # TODO: also maybe do color in pango?

        return out, rendered.width, rendered.rows

    def set(self, text: str):
        assert not self.ctx.closed, 'conn is closed'

        self.text = text
        rendered, width, height = self.render()

        if height != self.height or width != self.width or not self.image:
            new = Image(self.ctx, self.win, None, width, height, self.x, self.y)
            if self.image:
                self.image.destroy()
            self.image = new

        self.image.set(rendered)

        self.width, self.height = width, height

    def draw(self):
        assert not self.ctx.closed, 'conn is closed'

        if self.image:
            self.image.draw()

    def destroy(self):
        assert not self.ctx.closed, 'conn is closed'

        if self.image:
            self.image.destroy()

    def move(self, x: int, y: int):
        self.x = x
        self.y = y
        if self.image:
            self.image.x = x
            self.image.y = y


@applyPre
class Rectangle(
    GRectangle
):  # ? maybe implement this for any polygon and then just use that for a rectangle

    def __init__(
        self,
        ctx: 'Ctx[GCtx]',
        window: 'GWindow',
        x: int,
        y: int,
        width: int,
        height: int,
        color: int = 0x000000,
    ) -> None:
        assert not ctx.closed, 'conn is closed'

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.window = window
        self.ctx = ctx
        self.rect = rectangle({'x': x, 'y': y, 'width': width, 'height': height})

        self.gc = xcb.xcbGenerateId(ctx.gctx.connection)

        mask = xcb.XCBGcForeground
        args = uintarr([color])

        xcb.xcbCreateGc(ctx.gctx.connection, self.gc, window.id, mask, args)

    def draw(self):
        assert not self.ctx.closed, 'conn is closed'

        xcb.xcbPolyFillRectangle(
            self.ctx.gctx.connection, self.window.id, self.gc, 1, self.rect
        )

        xcb.xcbFlush(self.ctx.gctx.connection)

    def resize(self, width: int, height: int):
        assert not self.ctx.closed, 'conn is closed'

        self.rect.width = width
        self.rect.height = height

    def move(self, x: int, y: int):
        self.rect.x = x
        self.rect.y = y
