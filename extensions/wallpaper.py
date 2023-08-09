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
        
        img:np.ndarray = cv2.imread(self.wall)
        img = cv2.resize(img, (ctx.screen.width_in_pixels, ctx.screen.height_in_pixels))
        self.height, self.width, px = img.shape
        data = []
        for row in img:
            for pixel in row:
                data.append(pixel[0])
                data.append(pixel[1])
                data.append(pixel[2])
                data.append(0xff)
        data = np.array(data, dtype=np.uint8)
        self.gc = xcb.xcb_generate_id(ctx.connection)
        self.pixmap = xcb.xcb_generate_id(ctx.connection)
        xcb.xcb_create_pixmap(ctx.connection, ctx.screen.root_depth, self.pixmap, ctx._root, self.width, self.height)
        xcb.xcb_create_gc(ctx.connection, self.gc, self.pixmap, 0, ffi.NULL)
        self.image = xcb.xcb_image_create_native(ctx.connection, self.width, self.height,
                                                 xcb.XCB_IMAGE_FORMAT_Z_PIXMAP, ctx.screen.root_depth, ffi.NULL,
                                                 self.width * self.height * 4,
                                                 uchararr(data.tobytes()))
        xcb.xcb_image_put(ctx.connection, self.pixmap, self.gc, self.image, 0, 0, 0)
        self.draw()

    def draw(self):
        xcb.xcb_copy_area(self.ctx.connection, self.pixmap, self.ctx._root, self.gc, 0, 0, 0, 0, self.width, self.height)
        xcb.xcb_flush(self.ctx.connection)