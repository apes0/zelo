from .types import uchararr
import cv2
import numpy as np
from xcb_cffi import ffi, lib
from ..generic import GImage

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
        ) // lib.xcb_get_maximum_request_length(ctx.connection) + 1
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


# TODO: make these 2


class Text:
    def __init__(self) -> None:
        raise NotImplementedError


class Rectangle:
    def __init__(self) -> None:
        raise NotImplementedError
