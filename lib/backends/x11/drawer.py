from .types import uchararr, chararr, uintarr, rectangle
import cv2
import numpy as np
from html import escape
from xcb_cffi import ffi, lib
from cairo_cffi.lib import render
from ..generic import CData, GImage, GWindow, GRectangle, GText

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...ctx import Ctx
    from .window import Window

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

        self.gc = lib.xcb_generate_id(ctx.connection)
        self.pixmap = lib.xcb_generate_id(ctx.connection)

        self.image: CData

        lib.xcb_create_pixmap(
            ctx.connection,
            ctx.screen.screen.root_depth,
            self.pixmap,
            self.windowId,
            self.width,
            self.height,
        )

        lib.xcb_create_gc(ctx.connection, self.gc, self.pixmap, 0, ffi.NULL)

        if img is not None:
            self.set(img)

    def set(self, img):
        img = cv2.resize(img, (self.width, self.height))

        _, _, px = img.shape

        if px == 3:
            img = np.dstack(
                (img, np.ones((self.height, self.width, 1), dtype=np.uint8) * 255)
            )
        self.parts = (
            self.width * self.height * 4
        ) // lib.xcb_get_maximum_request_length(self.ctx.connection) + 2
        # this works with +2 for some reason
        pos = 0
        prev = 0
        size = self.height / self.parts

        for _ in range(self.parts):
            # TODO: use the scanline_pad stuff
            pos += size
            self.image = lib.xcb_image_create_native(
                self.ctx.connection,
                self.width,
                round(pos) - round(prev),
                lib.XCB_IMAGE_FORMAT_Z_PIXMAP,
                self.ctx.screen.screen.root_depth,
                ffi.NULL,
                self.width * (round(pos) - round(prev)) * 4,
                uchararr(img[round(prev) : round(pos), :, :].tobytes()),
            )

            lib.xcb_image_put(
                self.ctx.connection, self.pixmap, self.gc, self.image, 0, round(prev), 0
            )

            prev = pos
        lib.xcb_flush(self.ctx.connection)

    def draw(self):
        lib.xcb_copy_area(
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

        lib.xcb_flush(self.ctx.connection)

    def destroy(self):
        lib.xcb_image_destroy(self.image)
        lib.xcb_flush(self.ctx.connection)

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

        self.gc = lib.xcb_generate_id(ctx.connection)

        mask = lib.XCB_GC_FOREGROUND
        args = uintarr([color])

        lib.xcb_create_gc(ctx.connection, self.gc, window.id, mask, args)

    def draw(self):
        lib.xcb_poly_fill_rectangle(
            self.ctx.connection, self.window.id, self.gc, 1, self.rect
        )

        lib.xcb_flush(self.ctx.connection)

    def resize(self, width: int, height: int):
        self.rect.width = width
        self.rect.height = height

    def move(self, x: int, y: int):
        self.rect.x = x
        self.rect.y = y
