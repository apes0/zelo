from ..backends.ffi import load
from..backends.generic import *
loaded = load("screen")

Screen: type[GScreen] = loaded.Screen
