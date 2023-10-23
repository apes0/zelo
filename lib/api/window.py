from ..backends.ffi import load
from ..backends.generic import *

loaded = load("window")

Window: type[GWindow] = loaded.Window
