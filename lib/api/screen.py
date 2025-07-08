from ..backends.ffi import load
from ..backends.generic import *

loaded = load("screen")

Screen: type[GScreen] = loaded.Screen
# sources:
#lib.backends.standalone.screen
#lib.backends.wayland.screen
#lib.backends.x11.screen
Display: type[GDisplay] = loaded.Display
# sources:
#lib.backends.standalone.screen
#lib.backends.wayland.screen
#lib.backends.x11.screen
