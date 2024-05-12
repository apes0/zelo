from .types import uchararr, chararr, uintarr, rectangle
import cv2
import numpy as np
from html import escape
from .. import xcb
from ..cairo import render
from xcb_cffi import ffi
from ..generic import GImage, GWindow, GRectangle, GText

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...ctx import Ctx
    from .window import Window
    from .gctx import GCtx

# Create gcontext and such here
# do text rendering, image drawing, etc.


class Image(GImage):
    def __init__(
        self,
        ctx: 'Ctx',
        window: 'Window',
        img: np.ndarray | None,
        width: int,
        height: int,
        x: int,
        y: int,
    ) -> None:
        self.x: int = x
        self.y: int = y

        self.ctx = ctx

        self.windowId = window.id

        self.width = width
        self.height = height

        self.gc = xcb.xcbGenerateId(ctx.connection)
        self.pixmap = xcb.xcbGenerateId(ctx.connection)

        self.image: xcb.XcbImageT
        self.useShm = ctx.gctx.avail('MIT-SHM') # type: ignore

        if self.useShm:
            self.shm = self.shm = xcb.createShm(self.ctx.connection, self.width * self.height * 4)

            xcb.xcbShmCreatePixmap(
                self.ctx.connection, 
                self.pixmap, 
                self.windowId, 
                self.width, 
                self.height, 
                ctx.screen.screen.rootDepth, 
                self.shm.id,
                0
            )
        else:
            xcb.xcbCreatePixmap(
                ctx.connection,
                ctx.screen.screen.rootDepth,
                self.pixmap,
                self.windowId,
                self.width,
                self.height,
            )

        xcb.xcbCreateGc(ctx.connection, self.gc, self.pixmap, 0, xcb.NULL)

        if img is not None:
            self.set(img)

    def set(self, img):
        img = cv2.resize(img, (self.width, self.height))

        _, _, px = img.shape

        if px == 3:
            img = np.dstack(
                (img, np.ones((self.height, self.width, 1), dtype=np.uint8) * 255)
            )

        if self.useShm: # type: ignore
            data = img.tobytes()
            ffi.memmove(self.shm.addr, data, len(data))

        else:
            parts = (self.width * self.height * 4) // xcb.xcbGetMaximumRequestLength(
                self.ctx.connection
            ) + 2
            # this works with +2 for some reason
            pos = 0
            prev = 0
            size = self.height / parts

            for _ in range(parts):
                # TODO: use the.scanlinePad stuff
                pos += size
                self.image = xcb.xcbImageCreateNative(
                    self.ctx.connection,
                    self.width,
                    round(pos) - round(prev),
                    xcb.XCBImageFormatZPixmap,
                    self.ctx.screen.screen.rootDepth,
                    xcb.NULL,
                    self.width * (round(pos) - round(prev)) * 4,
                    uchararr(img[round(prev) : round(pos), :, :].tobytes()),
                )

                xcb.xcbImagePut(
                    self.ctx.connection, self.pixmap, self.gc, self.image, 0, round(prev), 0
                )

                prev = pos

        xcb.xcbFlush(self.ctx.connection)

    def draw(self):
        xcb.xcbCopyArea(
            self.ctx.connection,
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

        xcb.xcbFlush(self.ctx.connection)

    def destroy(self):
        if self.useShm:
            xcb.removeShm(self.ctx.connection, self.shm)
        else:
            xcb.xcbImageDestroy(self.image)

        xcb.xcbFreePixmap(self.ctx.connection, self.pixmap)
        xcb.xcbFlush(self.ctx.connection)

    def move(self, x: int, y: int):
        self.x = x
        self.y = y


class Text(GText):
    def __init__(
        self,
        ctx: 'Ctx',
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
        if self.image:
            self.image.draw()

    def destroy(self):
        if self.image:
            self.image.destroy()

    def move(self, x: int, y: int):
        self.x = x
        self.y = y
        if self.image:
            self.image.x = x
            self.image.y = y


class Rectangle(
    GRectangle
):  # ? maybe implement this for any polygon and then just use that for a rectangle
    def __init__(
        self,
        ctx: 'Ctx',
        window: 'GWindow',
        x: int,
        y: int,
        width: int,
        height: int,
        color: int = 0x000000,
    ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.window = window
        self.ctx = ctx
        self.rect = rectangle({'x': x, 'y': y, 'width': width, 'height': height})

        self.gc = xcb.xcbGenerateId(ctx.connection)

        mask = xcb.XCBGcForeground
        args = uintarr([color])

        xcb.xcbCreateGc(ctx.connection, self.gc, window.id, mask, args)

    def draw(self):
        xcb.xcbPolyFillRectangle(
            self.ctx.connection, self.window.id, self.gc, 1, self.rect
        )

        xcb.xcbFlush(self.ctx.connection)

    def resize(self, width: int, height: int):
        self.rect.width = width
        self.rect.height = height

    def move(self, x: int, y: int):
        self.rect.x = x
        self.rect.y = y
