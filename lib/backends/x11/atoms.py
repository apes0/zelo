import struct
from typing import TYPE_CHECKING, Any, Callable

import numpy as np

from lib.backends.x11 import requests

from .. import xcb
from .types import charpC, maxUVal, icccmWmHintsTC

if TYPE_CHECKING:
    from lib.backends.x11.window import Window
    from lib.ctx import Ctx

atoms = {
    'WM_NAME': (xcb.XCBAtomWmName, xcb.XCBAtomString),
    'WM_ICON_NAME': (xcb.XCBAtomWmIconName, xcb.XCBAtomString),
    '_NET_WM_ICON': (None, xcb.XCBAtomCardinal),
    'WM_HINTS': (xcb.XCBAtomWmHints, xcb.XCBAtomWmHints),
}

readers: dict[str, Callable[['Atom'], Any]] = {}


def reader(t: str):
    def deco(fn: Callable[['Atom'], Any]):
        readers[t] = fn

    return deco


class Atom:
    def __init__(self, ctx: 'Ctx', win: 'Window', name: str) -> None:
        self.ctx = ctx
        self.win = win
        self.name = name
        self.value: Any = None

        from ..events import Event

        self.changed = Event('atomChanged')

        atom = atoms[name]

        self.id = atom[0]
        self.type = atom[1]

        gctx = self.ctx._getGCtx()
        gctx.atoms[self.win.id] = {**gctx.atoms.get(self.win.id, {}), self.id: self}

    async def read(self):
        self.value = await readers[self.name](self)
        await self.changed.trigger(self.ctx)
        # print(f'read {self.value}')

    async def _read(self, off: int = 0, buf: int = maxUVal('int')):
        # NOTE: buf and off are "32-bit multiples", so if you want 4 bytes, you should use a buf of 1
        conn = self.ctx._getGCtx().connection

        resp = await requests.GetProperty(
            self.ctx, conn, 0, self.win.id, self.id, self.type, 0, buf
        ).reply()

        if resp == xcb.NULL:
            return 0, xcb.NULL

        return resp.valueLen, xcb.xcbGetPropertyValue(resp)


async def readString(atom: Atom):
    out = b''

    read, data = await atom._read()

    if not read:
        # basically just if its empty
        return out.decode()

    data = charpC(data.obj)
    for n in range(read):
        out += data[n]

    return out.decode()


readers['WM_NAME'] = readString
readers['WM_ICON_NAME'] = readString


# ?: does anybody set this or do they use the icon pixmap from the wm hints?
@reader('_NET_WM_ICON')
async def readIcon(atom: Atom):
    # TODO: look for the biggest icon rather than just picking the 1st one
    print('reading icon!!!')
    read, data = await atom._read()
    data = charpC(data.obj)

    if not read:
        return None

    w = struct.unpack('!I', data[0:4])[0]
    h = struct.unpack('!I', data[4:8])[0]

    print(w, h)

    img = np.frombuffer(data[8 : 8 + w * h * 4], dtype=np.uint8)
    img.shape = (h, w, 4)

    print(img)

    return img


class Hints:
    def __init__(self):
        self.icon = None


@reader('WM_HINTS')
async def readHints(atom: Atom):
    hints = atom.value or Hints()

    read, data = await atom._read()
    obj = xcb.XcbIcccmWmHintsT(icccmWmHintsTC(data))

    if obj.flags & xcb.XCBIcccmWmHintIconPixmap:
        # we have an icon!
        g = await requests.GetGeometry(
            atom.ctx, atom.ctx._getGCtx().connection, obj.iconPixmap
        ).reply()

        w, h = g.width, g.height

        i = await requests.GetImage(
            atom.ctx,
            atom.ctx._getGCtx().connection,
            xcb.XCBImageFormatZPixmap,
            obj.iconPixmap,
            0,
            0,
            w,
            h,
            maxUVal('int'),
        ).reply()

        dat = xcb.xcbGetImageData(i)

        depth: int = xcb.xcbGetImageDataLength(i) // (w * h)  # TODO: same as above here

        buf = xcb.ffi.buffer(dat.obj, w * h * depth)
        out: np.ndarray = np.frombuffer(buf, np.uint8)

        hints.icon = out.reshape((h, w, depth))

    return hints

    # TODO: support everything else lol
