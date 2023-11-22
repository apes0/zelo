from .types import uchararr, chararr, uintarr, rectangle
import cv2
import numpy as np
from xcb_cffi import ffi, lib
from ..generic import GImage, GWindow, GRectangle

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
        imgPath: str,
        width: int,
        height: int,
        x: int,
        y: int,
    ) -> None:
        self.x = x
        self.y = y

        self.ctx = ctx

        self.windowId = window.id

        img: np.ndarray = cv2.imread(imgPath)
        img = cv2.resize(img, (width, height))

        self.height, self.width, px = img.shape

        if px == 3:
            img = np.dstack(
                (img, np.ones((self.height, self.width, 1), dtype=np.uint8) * 255)
            )

        self.gc = lib.xcb_generate_id(ctx.connection)
        self.pixmap = lib.xcb_generate_id(ctx.connection)

        lib.xcb_create_pixmap(
            ctx.connection,
            ctx.screen.screen.root_depth,
            self.pixmap,
            self.windowId,
            self.width,
            self.height,
        )

        lib.xcb_create_gc(ctx.connection, self.gc, self.pixmap, 0, ffi.NULL)

        self.parts = (
            self.width * self.height * 4
        ) // lib.xcb_get_maximum_request_length(ctx.connection) + 2
        # this works with +2 for some reason
        pos = 0
        prev = 0
        size = self.height / self.parts

        for _ in range(self.parts):
            # TODO: use the scanline_pad stuff
            pos += size
            image = lib.xcb_image_create_native(
                ctx.connection,
                self.width,
                round(pos) - round(prev),
                lib.XCB_IMAGE_FORMAT_Z_PIXMAP,
                ctx.screen.screen.root_depth,
                ffi.NULL,
                self.width * (round(pos) - round(prev)) * 4,
                uchararr(img[round(prev) : round(pos), :, :].tobytes()),
            )

            lib.xcb_image_put(
                ctx.connection, self.pixmap, self.gc, image, 0, round(prev), 0
            )

            prev = pos
        self.draw()

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


class Text:
    def __init__(
        self,
        ctx: 'Ctx',
        window: 'Window',
        _font: str,
        text: str,
        x: int,
        y: int,
        fore: int | None = None,
        back: int | None = None,
    ) -> None:
        # https://www.x.org/releases/X11R7.7/doc/libxcb/tutorial/index.html#font
        # NOTE: as it says here, use xlsfonts for a list of fonts
        font = lib.xcb_generate_id(ctx.connection)

        lib.xcb_open_font(
            ctx.connection,
            font,
            len(_font),
            chararr(_font.encode()),
        )

        self.x = x
        self.y = y
        self.text = text
        self.ctx = ctx
        self.window = window

        self.gc = lib.xcb_generate_id(ctx.connection)
        mask = lib.XCB_GC_FOREGROUND | lib.XCB_GC_BACKGROUND | lib.XCB_GC_FONT

        args = uintarr(
            [
                fore if fore else ctx.screen.screen.black_pixel,
                back if back else ctx.screen.screen.white_pixel,
                font,
            ]
        )
        lib.xcb_create_gc(ctx.connection, self.gc, window.id, mask, args)
        lib.xcb_close_font(ctx.connection, font)
        self.draw()

    def draw(self):
        # TODO: split the text if its too big
        # TODO: add support for more characters (with xcb_image_text_16)
        # TODO: more fonts
        lib.xcb_image_text_8(
            self.ctx.connection,
            len(self.text),
            self.window.id,
            self.gc,
            self.x,
            self.y,
            chararr(self.text.encode()),
        )

        lib.xcb_flush(self.ctx.connection)


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

        self.draw()

    def draw(self):
        lib.xcb_poly_fill_rectangle(
            self.ctx.connection, self.window.id, self.gc, 1, self.rect
        )

        lib.xcb_flush(self.ctx.connection)
