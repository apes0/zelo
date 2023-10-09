from ..backends.ffi import load
from..backends.generic import *
loaded = load("keys")

Mod: type[GMod] = loaded.Mod
Key: type[GKey] = loaded.Key
