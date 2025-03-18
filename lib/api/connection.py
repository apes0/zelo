from ..backends.ffi import load
from ..backends.generic import *

loaded = load("connection")

Connection: type[GConnection] = loaded.Connection
# sources:
#lib.backends.wayland.connection
#lib.backends.x11.connection
