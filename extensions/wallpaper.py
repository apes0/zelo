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

        if not self.video:
            self.img: GImage = Image(
                ctx,
                ctx.root,
                cv2.imread(self.wall),
                self.display.width,
                self.display.height,
                self.display.x,
                self.display.y,
            )

            self.img.draw()

        else:
            cap = cv2.VideoCapture(self.wall)
            self.fps = cap.get(cv2.CAP_PROP_FPS)
            ret = True
            self.frames: list[GImage] = []

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                self.frames.append(
                    Image(
                        self.ctx,
                        self.ctx.root,
                        frame,
                        self.display.width,
                        self.display.height,
                        self.display.x,
                        self.display.y,
                    )
                )

            cap.release()
            ctx.nurs.start_soon(self.drawVideo)

        createNotify.addListener(self.drawImg)
        mapRequest.addListener(self.drawImg)
        unmapNotify.addListener(self.drawImg)
        destroyNotify.addListener(self.drawImg)

    async def drawImg(self, *a):
        self.img.draw()

    async def drawVideo(self, *a):
        while True:
            for frame in self.frames:
                self.img = frame
                self.img.draw()
                await trio.sleep(1 / self.fps)
