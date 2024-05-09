import traceback
from lib.api.drawer import Image
from lib.extension import Extension
from lib.backends.events import mapNotify, unmapNotify
from typing import TYPE_CHECKING
import numpy as np
import struct
import trio
import zlib
from base64 import urlsafe_b64encode, urlsafe_b64decode
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, load_pem_public_key
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
# grr i hate this lol

if TYPE_CHECKING:
    from lib.backends.generic import GWindow
    from lib.ctx import Ctx

# share wins to other systems
# NOTE: requires ``cryptography`` module
# NOTE: this will run well only when shm is added, so it will not be documented untill then

# TODO: shortcut for sharing/unsharing
# TODO: io for wins
# TODO: resize win when sending
# TODO: if the size of our window and the other window do not match, add a filler/make that part transparent
# TODO: permission config on the server
# TODO: clean up this mess
# TODO: exclude/fetch window shortcuts on the client
# TODO: client shortcut to sent io to the root window on the server
# FIXME: memory leaks somewhere???

# This is how it works (from the server side):
# First, we generate a public and private rsa key
# We send the public one to the client
# We receive back the password, encrypted with the public key
# We decrypt it and compare it with our own
# If they don't match, close the connection
# Otherwise, we read the client's next message, containing its own rsa public key
# We send it our fernet key encrypted with its own public key, and it sends us its fernet key encrypted with our public key
# We xor them, and use that as the actual fernet key
# Finally, we enter a loop where we send (encrypted) window info until the client disconnects

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

# NOTE: we regenerate the rsa key for every connection
# That makes it impossible to just capture the message containing the password and reuse it
# If we didn't, the you could just listen for the message with the password and repeat it, because it uses the same public key

defPort = 3315 # eels lol

def encryptRsa(pub: rsa.RSAPublicKey, data: bytes):
    return pub.encrypt(data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def decryptRsa(priv: rsa.RSAPrivateKey, data: bytes):
    return priv.decrypt(data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def genKeys():
    priv = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    pub = priv.public_key()
    pubBytes = pub.public_bytes(
        Encoding.PEM,
        PublicFormat.PKCS1
    )
    return priv, pub, pubBytes

def xorb(b1: bytes, b2: bytes):
    # https://stackoverflow.com/a/71302551
    # thanks man, love ya
    a = np.frombuffer(b1, dtype = np.uint8)
    b = np.frombuffer(b2, dtype = np.uint8)
    return (a^b).tobytes()

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

class ShareServer(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.port = defPort
        self.auth: bytes = b''
        self.wins: list['GWindow'] = []
        self.rate = 1/10
        self.running = False
        self.event = trio.Event()
        self.msgs: dict[int, bytes] = {}

        super().__init__(ctx, cfg)

        self.addListener(mapNotify, self.map)
        self.addListener(unmapNotify, self.unmap)
        ctx.nurs.start_soon(self.serve)

    async def serve(self):
        async def _serve(stream: trio.SocketStream):
            # generate the keys
            myPriv, myPub, myPubBytes = genKeys()

            await send(stream, myPubBytes) # send the pubkey
            auth = decryptRsa(myPriv, await recv(stream)) # recieve the auth
            
            if auth != self.auth: # check the auth
                await stream.aclose()
                return

            clientPub: rsa.RSAPublicKey
            clientPub = load_pem_public_key(await recv(stream)) # type: ignore
            clientKey = decryptRsa(myPriv, await recv(stream)) # get the client's fkey

            myKey = urlsafe_b64decode(Fernet.generate_key()) # generate my own key
            await send(stream, encryptRsa(clientPub, myKey)) # send encrypted fernet key
            
            key = xorb(clientKey, myKey)
            print(urlsafe_b64encode(key), len(urlsafe_b64encode(key)))
            fernet = Fernet(urlsafe_b64encode(key))

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

        ctx.nurs.start_soon(self.connect)

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
        serverPub = load_pem_public_key(await recv(stream)) # type: ignore
        serverPub: rsa.RSAPublicKey

        await send(stream, encryptRsa(serverPub, self.auth)) # send the auth encrypted with the server's key
        
        myPriv, myPub, myPubBytes = genKeys() # generate our own keys
        myKey = urlsafe_b64decode(Fernet.generate_key()) # No mikey, thats so not right

        await send(stream, myPubBytes) # ? do we need to encrypt here?
        await send(stream, encryptRsa(serverPub, myKey)) # encrypt with the server's key

        serverKey = decryptRsa(myPriv, await recv(stream)) # decrypt with our own key
        key = xorb(serverKey, myKey)
        print(len(serverKey), len(myKey), len(key))
        print(urlsafe_b64encode(key), len(urlsafe_b64encode(key)))
        fernet = Fernet(urlsafe_b64encode(key))

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
