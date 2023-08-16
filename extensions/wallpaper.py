from lib.extension import Extension
from typing import TYPE_CHECKING
from lib.ffi import ffi, lib as xcb
from lib.types import uchararr
import cv2
import numpy as np

if TYPE_CHECKING:
    from lib.ctx import Ctx


class Wallpaper(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        super().__init__(ctx, cfg)
        self.wall: str
        self.addListener(xcb.XCB_CREATE_NOTIFY, lambda *a: self.draw())
        self.addListener(xcb.XCB_MAP_REQUEST, lambda *a: self.draw())
        self.addListener(xcb.XCB_UNMAP_NOTIFY, lambda *a: self.draw())
        self.addListener(xcb.XCB_CONFIGURE_NOTIFY, lambda *a: self.draw())

        img: np.ndarray = cv2.imread(self.wall)
        img = cv2.resize(img, (ctx.screen.width_in_pixels, ctx.screen.height_in_pixels))
        self.height, self.width, px = img.shape
        if px == 3:
            img = np.dstack(
                (img, np.ones((self.height, self.width, 1), dtype=np.uint8) * 255)
            )
        self.gc = xcb.xcb_generate_id(ctx.connection)
        self.pixmap = xcb.xcb_generate_id(ctx.connection)
        xcb.xcb_create_pixmap(
            ctx.connection,
            ctx.screen.root_depth,
            self.pixmap,
            ctx._root,
            self.width,
            self.height,
        )
        xcb.xcb_create_gc(ctx.connection, self.gc, self.pixmap, 0, ffi.NULL)
        self.parts = (
            self.width * self.height * 4
        ) // xcb.xcb_get_maximum_request_length(ctx.connection) + 1
        pos = 0
        prev = 0
        size = self.height / self.parts
        for _ in range(self.parts):
            # TODO: use the scanline_pad stuff
            pos += size
            image = xcb.xcb_image_create_native(
                ctx.connection,
                self.width,
                round(pos) - round(prev),
                xcb.XCB_IMAGE_FORMAT_Z_PIXMAP,
                ctx.screen.root_depth,
                ffi.NULL,
                self.width * (round(pos) - round(prev)) * 4,
                uchararr(img[round(prev) : round(pos), :, :].tobytes()),
            )
            xcb.xcb_image_put(
                ctx.connection, self.pixmap, self.gc, image, 0, round(prev), 0
            )
            print(image, pos, prev, self.parts)
            prev = pos
        self.draw()

    def draw(self):
        xcb.xcb_copy_area(
            self.ctx.connection,
            self.pixmap,
            self.ctx._root,
            self.gc,
            0,
            0,
            0,
            0,
            self.width,
            self.height,
        )
        xcb.xcb_flush(self.ctx.connection)
