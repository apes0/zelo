from lib.extension import Extension, perDisplay
from typing import TYPE_CHECKING
from lib.backends.events import createNotify, mapRequest, unmapNotify, destroyNotify
from lib.api.drawer import Image
import cv2
import trio

if TYPE_CHECKING:
    from lib.ctx import Ctx
    from lib.backends.generic import GImage, GDisplay


# TODO: slower for video with perDisplay with more and more displays


@perDisplay
class Wallpaper(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.wall: str
        self.display: GDisplay
        self.video = False
        super().__init__(ctx, cfg)

        self.img = Image(
            self.ctx,
            self.ctx.root,
            None,
            self.display.width,
            self.display.height,
            self.display.x,
            self.display.y,
        )

        if not self.video:
            self.img.set(cv2.imread(self.wall))
            self.img.draw()
        else:
            self.cap = cv2.VideoCapture(self.wall)
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)

            ctx.nurs.start_soon(self.drawVideo)

        createNotify.addListener(self.drawImg)
        mapRequest.addListener(self.drawImg)
        unmapNotify.addListener(self.drawImg)
        destroyNotify.addListener(self.drawImg)

    async def drawImg(self, *a):
        self.img.draw()

    async def drawVideo(self, *a):
        cur = trio.current_time()
        while True:
            await trio.sleep_until(cur := cur + 1 / self.fps)
            ret, frame = self.cap.read()

            if not ret:
                # idk how good this is but works well so its whatever :)
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            self.img.set(frame)
            self.img.draw()
