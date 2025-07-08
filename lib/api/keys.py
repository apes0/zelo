from ..backends.ffi import load
from ..backends.generic import *

loaded = load("keys")

Mod: type[GMod] = loaded.Mod
# sources:
#lib.backends.standalone.keys
#lib.backends.wayland.keys
#lib.backends.x11.keys
Key: type[GKey] = loaded.Key
# sources:
#lib.backends.standalone.keys
#lib.backends.wayland.keys
#lib.backends.x11.keys
