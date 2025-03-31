from lib.backends.x11 import requests
from .types import charpC
from typing import TYPE_CHECKING, Any
from .. import xcb
import math

if TYPE_CHECKING:
    from lib.backends.x11.window import Window
    from lib.ctx import Ctx

atoms = {
    'WM_NAME': (xcb.XCBAtomWmName, xcb.XCBAtomString),
}

readers = {}


def reader(t):
    def deco(fn):
        readers[t] = fn

    return deco


class Atom:
    def __init__(self, ctx: 'Ctx', win: 'Window', name: str) -> None:
        self.ctx = ctx
        self.win = win
        self.value: Any = None

        if atom := atoms.get(name):
            self.id = atom[0]
            self.type = atom[1]
        else:
            # TODO: run a lookup here
            # and maybe cache it
            pass

        gctx = ctx._getGCtx()
        gctx.atoms[win.id] = {**gctx.atoms.get(win.id, {}), self.id: self}

        from ..events import Event

        self.changed = Event('atomChanged')

    async def read(self):
        self.value = await readers[self.type](self)
        await self.changed.trigger(self.ctx)
        # print(f'read {self.value}')

    async def _read(self, off: int = 0, buf: int = 4):
        # NOTE: buf and off are "32-bit multiples", so if you want 4 bytes, you should use a buf of 1
        conn = self.ctx._getGCtx().connection

        resp = await requests.GetProperty(
            self.ctx, conn, 0, self.win.id, self.id, self.type, off, buf
        ).reply()

        if resp == xcb.NULL:
            return 0, xcb.NULL

        return resp.valueLen, xcb.xcbGetPropertyValue(resp)


@reader(xcb.XCBAtomString)
async def readString(atom: Atom):
    out = b''

    pos = 0

    while True:
        read, data = await atom._read(off=pos)

        if not read:
            # basically just if its empty
            return out.decode()

        data = charpC(data.obj)
        for n in range(read):
            c = data[n]
            if c == b'\x00':
                return out.decode()

            out += data[n]

        pos += math.ceil(read / 4)
