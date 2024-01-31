from lib.extension import Extension, single
from typing import TYPE_CHECKING
from lib.backends.events import redraw
from lib.api.drawer import Image, Text
import cv2
import trio

if TYPE_CHECKING:
    from lib.ctx import Ctx
    from lib.backends.generic import GImage, GWindow

# TODO: support multiple wallpapers for each screen


@single
class Wallpaper(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.wall: str
        self.video = False
        super().__init__(ctx, cfg)

        self.imgs: list[GImage] = [
            Image(
                self.ctx,
                self.ctx.root,
                None,
                display.width,
                display.height,
                display.x,
                display.y,
            )
            for display in ctx.screen.displays
        ]

        if not self.video:
            _img = cv2.imread(self.wall)
            for img in self.imgs:
                img.set(_img)
                img.draw()
            del _img
        else:
            self.cap = cv2.VideoCapture(self.wall)
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)

            ctx.nurs.start_soon(self.drawVideo)

        redraw.addListener(self.drawImg)

    async def drawImg(self, win: 'GWindow'):
        if win.id != self.ctx._root:
            return

        for img in self.imgs:
            img.draw()

    async def drawVideo(self, *a):
        cur = trio.current_time()
        while True:
            ret, frame = self.cap.read()

            if not ret:
                # idk how good this is but works well so its whatever :)
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            for img in self.imgs:
                img.set(frame)
                img.draw()

            await trio.sleep_until(cur := cur + 1 / self.fps)
