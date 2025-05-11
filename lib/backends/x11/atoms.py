import struct
from typing import TYPE_CHECKING, Any, Callable

import numpy as np

from lib.backends.x11 import requests
from lib.debcfg import log, DEBUG

from .. import xcb
from .types import charpC, maxUVal, icccmWmHintsTC, voidpC, intpC

if TYPE_CHECKING:
    from lib.backends.generic import GWindow
    from lib.ctx import Ctx

# atom name: id or None, type, atom format
atoms: dict[str, tuple[int | None, int, int]] = {
    'WM_NAME': (xcb.XCBAtomWmName, xcb.XCBAtomString, 8),
    '_NET_WM_NAME': (None, xcb.XCBAtomString, 8),
    'WM_ICON_NAME': (xcb.XCBAtomWmIconName, xcb.XCBAtomString, 0),
    '_NET_WM_ICON': (None, xcb.XCBAtomCardinal, 0),
    '_NET_SUPPORTING_WM_CHECK': (None, xcb.XCBAtomWindow, 32),
    'WM_HINTS': (xcb.XCBAtomWmHints, xcb.XCBAtomWmHints, 0),
    '_NET_CLIENT_LIST': (None, xcb.XCBAtomWindow, 32),
    '_NET_WM_STATE': (None, xcb.XCBAtomAtom, 0),
    '_NET_WM_STATE_FULLSCREEN': (None, xcb.XCBAtomAtom, 0),
}

readers: dict[str, Callable[['Atom'], Any]] = {}


def reader(t: str):
    def deco(fn: Callable[['Atom'], Any]):
        readers[t] = fn

    return deco


class Atom:
    def __init__(self, ctx: 'Ctx', win: 'GWindow', name: str) -> None:
        self.ctx: requests.Ctx = ctx
        self.win: 'GWindow' = win
        self.name: str = name
        self.value: Any = None
        self._set = False

        from ..events import Event

        self.changed = Event[()]('atomChanged')

        id, self.type, self.fmt = atoms[name]
        assert id != None, f'atom {name} missing id'
        self.id: int = id

        gctx = self.ctx._getGCtx()
        gctx.atoms[self.win.id] = {**gctx.atoms.get(self.win.id, {}), self.id: self}

    async def read(self):
        f = readers.get(self.name)

        if not f:
            return

        v = await f(self)

        # if self.value == v:
        #   return
        # TODO: numpy hates this and i hate it

        self.value = v
        await self.changed.trigger(self.ctx)
        # print(f'read {self.value}')

    async def _read(self, off: int = 0, buf: int = maxUVal('int')):
        # NOTE: buf and off are "32-bit multiples", so if you want 4 bytes, you should use a buf of 1
        conn = self.ctx._getGCtx().connection

        resp = await requests.GetProperty(
            self.ctx, conn, 0, self.win.id, self.id, self.type, off, buf
        ).reply()

        if resp == xcb.NULL:
            return 0, xcb.NULL

        return resp.valueLen, xcb.xcbGetPropertyValue(resp)

    async def set(self, data, size: int, mode=xcb.XCBPropModeReplace):
        log(
            'backend',
            DEBUG,
            f'setting {self.name} of {self.win.id} to {data} (size: {size})',
        )
        xcb.xcbChangeProperty(
            self.ctx._getGCtx().connection,
            mode,
            self.win.id,
            self.id,
            self.type,
            self.fmt,
            size,
            voidpC(data),
        )
        await self.changed.trigger(self.ctx)

    async def append(self, data, size: int):
        await self.set(data, size, xcb.XCBPropModeAppend)

    async def prepend(self, data, size: int):
        await self.set(data, size, xcb.XCBPropModePrepend)

    async def get(self):
        if not self._set:
            await self.read()
            self._set = True

        return self.value


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


@reader('_NET_WM_ICON')
async def readIcon(atom: Atom):
    # TODO: look for the biggest icon rather than just picking the 1st one
    # if you are debugging this: use firefox as a test app
    # i got the idea from
    # https://utcc.utoronto.ca/~cks/space/blog/unix/ModernXAppIcons

    read, data = await atom._read()
    data = charpC(data.obj)

    if not read:
        return None

    data = np.frombuffer(xcb.ffi.buffer(data, read * 4), dtype=np.uint8)

    w = struct.unpack('<I', data[0:4])[0]
    h = struct.unpack('<I', data[4:8])[0]

    img = data[8 : w * h * 4 + 8]

    img.shape = (h, w, 4)

    return np.roll(img, 4, axis=2) if img.size > 0 else None


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
