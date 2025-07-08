import struct
import traceback
import zlib
from base64 import urlsafe_b64decode, urlsafe_b64encode
from typing import TYPE_CHECKING

import numpy as np
import trio
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
    load_pem_private_key,
    load_pem_public_key,
)

from lib.api.drawer import Image
from lib.extension import Extension

# grr i hate this lol

if TYPE_CHECKING:
    from lib.backends.generic import GWindow
    from lib.ctx import Ctx

# share wins to other systems
# NOTE: requires ``cryptography`` module

# TODO: fix window closing (and other window operations in general)
# TODO: shortcut for sharing/unsharing
# TODO: io for wins
# TODO: resize win when sending
# TODO: if the size of our window and the other window do not match, add a filler/make that part transparent
# TODO: permission config on the server
# TODO: clean up this mess
# TODO: exclude/fetch window shortcuts on the client
# TODO: client shortcut to sent io to the root window on the server
# TODO: document this
# TODO: multicast announce that we are running:
# https://github.com/python-trio/trio/issues/537
# https://stackoverflow.com/questions/603852/how-do-you-udp-multicast-in-python
# FIXME: memory leaks when we dont use shm, must be something with screenshotting

# This is how it works (from the server side):
# We send a pregenerated public key to the client
# We receive back a fernet key, encrypted with the public key
# We send the client our own fernet key, encrypter with the client's fernet key
# Then we both xor the 2 keys we have
# This is the final Fernet key, from now on everything is encrypter with it
# We receive a password
# We compare it with our own
# If they don't match, close the connection
# Finally, we enter a loop where we send window info until the client disconnects

# NOTE: fernet inflates message by around 33% at the best case...
# source:

# import random
# import struct
# from cryptography.fernet import Fernet
# fernet = Fernet(Fernet.generate_key())

# for j in range(1, 25):
#     dat = b''
#     size = 100*j

#     for i in range(size):
#         dat += struct.pack('B', random.randint(0, 255))

#     print(len(fernet.encrypt(dat))/size)

defPort = 3315  # eels lol


def encryptRsa(pub: rsa.RSAPublicKey, data: bytes):
    return pub.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )


def decryptRsa(priv: rsa.RSAPrivateKey, data: bytes):
    return priv.decrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )


def genKeys():
    priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pub = priv.public_key()

    return priv, pub


def pubBytes(pub: rsa.RSAPublicKey):
    return pub.public_bytes(Encoding.PEM, PublicFormat.PKCS1)


def privBytes(priv: rsa.RSAPrivateKey):
    return priv.private_bytes(
        Encoding.PEM, PrivateFormat.PKCS8, encryption_algorithm=NoEncryption()
    )


def xorb(b1: bytes, b2: bytes):
    # https://stackoverflow.com/a/71302551
    # thanks man, love ya
    a = np.frombuffer(b1, dtype=np.uint8)
    b = np.frombuffer(b2, dtype=np.uint8)
    return (a ^ b).tobytes()


async def _recv(stream: trio.SocketStream, size):
    out = b''
    while size:
        recved = await stream.receive_some(size)
        assert recved, 'socked is dead'

        out = out + recved
        size -= len(recved)

    return out


async def send(stream: trio.SocketStream, data: bytes):
    await stream.send_all(struct.pack('I', len(data)) + data)


async def recv(stream: trio.SocketStream):
    l = struct.unpack('I', await _recv(stream, 4))[0]
    return await _recv(stream, l)


async def serverSwap(stream: trio.SocketStream, pubkey: str, privkey: str) -> Fernet:
    await send(stream, pubkey.encode())
    key = decryptRsa(load_pem_private_key(privkey.encode(), None), await recv(stream))
    _key = urlsafe_b64decode(Fernet.generate_key())
    fernet = Fernet(urlsafe_b64encode(key))
    await send(stream, fernet.encrypt(_key))

    return Fernet(urlsafe_b64encode(xorb(key, _key)))


async def clientSwap(stream: trio.SocketStream) -> Fernet:
    public = await recv(stream)
    key = Fernet.generate_key()

    await send(stream, encryptRsa(load_pem_public_key(public), urlsafe_b64decode(key)))
    fernet = Fernet(key)
    _key = fernet.decrypt(await recv(stream))

    return Fernet(urlsafe_b64encode(xorb(urlsafe_b64decode(key), _key)))


class ShareServer(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.port = defPort
        self.auth: bytes = b''
        self.wins: list[GWindow] = []
        self.rate = 1 / 10
        self.running = False
        self.event = trio.Event()
        self.msgs: dict[int, bytes] = {}

        super().__init__(ctx, cfg)

        self.addListener(ctx.mapNotify, self.map)
        self.addListener(ctx.unmapNotify, self.unmap)
        ctx.startSoon(self.serve)

    async def serve(self):
        try:
            self.pubkey = load_pem_public_key(await self.loadData('pubkey'))
            self.privkey = load_pem_private_key(await self.loadData('privkey'), None)
        except:
            self.privkey, self.pubkey = genKeys()
            await self.saveData('pubkey', pubBytes(self.pubkey))
            await self.saveData('privkey', privBytes(self.privkey))

        async def _serve(stream: trio.SocketStream):
            fernet = await serverSwap(
                stream, pubBytes(self.pubkey).decode(), privBytes(self.privkey).decode()
            )

            auth = fernet.decrypt(await recv(stream))

            if auth != self.auth:  # check the auth
                await stream.aclose()
                return

            await self.conn(fernet, stream)

        await trio.serve_tcp(_serve, self.port)

    async def conn(self, fernet: Fernet, stream: trio.SocketStream):
        while True:
            await self.event.wait()
            for id, msg in self.msgs.items():
                # TODO: check if id is ignored here
                msg = fernet.encrypt(msg)

                try:
                    await send(stream, msg)
                except:
                    # TODO: move this too logging (too lazy rn)
                    print(traceback.format_exc())
                    await stream.aclose()
                    return

    async def map(self, win: 'GWindow'):
        if win.ignore:
            return

        self.wins.append(win)

        if not self.running:
            await self.shooter()

    async def unmap(self, win: 'GWindow'):
        while win in self.wins:
            self.wins.remove(win)

    async def shooter(self):
        self.running = True
        time = trio.current_time()

        while self.wins:
            for win in self.wins:
                img = await win.screenshot()
                h, w, channels = np.shape(img)
                msg = struct.pack('IIII', win.id, w, h, channels) + zlib.compress(img)
                self.msgs[win.id] = msg

            self.event.set()
            self.event = trio.Event()

            await trio.sleep_until(time := time + self.rate)

        self.running = False


class ShareClient(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.port = defPort
        self.addr: str
        self.auth: bytes = b''
        self.imgs = {}
        self.retry = 60

        super().__init__(ctx, cfg)

        ctx.startSoon(self.connect)

    async def connect(self):
        while True:
            stream = await trio.open_tcp_stream(self.addr, self.port)

            if stream:
                try:
                    await self._connect(stream)
                except:
                    print(traceback.format_exc())
                    # TODO: log here

            await trio.sleep(self.retry)

    async def _connect(self, stream: trio.SocketStream):
        fernet = await clientSwap(stream)

        await send(stream, fernet.encrypt(self.auth))

        while True:
            data = fernet.decrypt(await recv(stream))
            id, w, h, channels = struct.unpack('IIII', data[:16])

            dat = np.frombuffer(zlib.decompress(data[16:]), np.uint8)
            dat = dat.reshape((h, w, channels))

            if not (img := self.imgs.get(id)):
                win = self.ctx.createWindow(0, 0, w, h, 0)

                img = Image(self.ctx, win, None, w, h, 0, 0)
                self.imgs[id] = img

                await win.map()

            if img.width != w or img.height != h:
                # resizing
                # TODO: move resizing to Image's set method
                win = self.ctx.getWindow(img.windowId)
                img.destroy()
                img = Image(self.ctx, win, dat, w, h, 0, 0)
                self.imgs[id] = img
            else:
                img.set(dat)

            img.draw()
