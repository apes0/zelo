import dbus
from .widget import Widget
from lib.api.drawer import Text, Rectangle
import trio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.ctx import Ctx


class Song:
    def __init__(self, name, artists, image):
        self.name: str = name
        self.artists: list[str] = artists
        self.image: str = image


def getSong():
    bus = dbus.SessionBus()
    for service in bus.list_names():
        if service.startswith('org.mpris.MediaPlayer2.'):
            player = bus.get_object(service, '/org/mpris/MediaPlayer2')
            status = player.Get(
                'org.mpris.MediaPlayer2.Player',
                'PlaybackStatus',
                dbus_interface='org.freedesktop.DBus.Properties',
            )

            if not status:
                continue

            metadata = player.Get(
                'org.mpris.MediaPlayer2.Player',
                'Metadata',
                dbus_interface='org.freedesktop.DBus.Properties',
            )

            if not metadata:
                continue

            return status, Song(
                name=metadata.get('xesam:title', '...'),
                artists=metadata.get('xesam:artist', []),
                image=metadata.get('mpris:artUrl', ''),
            )

    return None, None


class NowPlaying(Widget):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.fmt: str = '{song} - {artists}'
        self.update: float = 1 / 60
        self.step: float = 0.6  # px
        self.default = 'Nothing playing...'
        self.width: int = 200  # px
        self.font: str
        self.fore: int
        self.back: int

        super().__init__(ctx, cfg, resolve={'fore': int, 'back': int})

        self.text = Text(ctx, self.win, 0, 0, None, self.font, self.fore, self.back)
        self.rect = Rectangle(ctx, self.win, 0, 0, self.width, 1, self.back)
        ctx.nurs.start_soon(self._update)

    def getText(self):
        status, song = getSong()
        if not song:
            return self.default

        return self.fmt.format(song=song.name, artists=', '.join(song.artists))

    async def _update(self):
        prevs = ''
        cursor = 0
        ttime = trio.current_time()

        while True:
            text = self.getText()

            # restart when we see a new song
            if text != prevs:
                cursor = 0
                self.text.set(text)

                self.rect.resize(self.width, self.text.height)
                await self.setSize(self.width, self.text.height)

                prevs = text

            if cursor > self.text.width + self.width:
                cursor = 0

            cursor += self.step
            self.text.move(round(self.width - cursor), self.text.y)
            await self.draw()

            await trio.sleep_until(ttime := ttime + self.update)

    async def draw(self):
        self.rect.draw()
        self.text.draw()
