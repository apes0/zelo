from ..backends.ffi import load
from ..backends.generic import *

loaded = load("window")

Window: type[GWindow] = loaded.Window
# sources:
#lib.backends.standalone.window
#lib.backends.wayland.window
#lib.backends.x11.window
