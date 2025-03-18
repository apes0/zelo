from ..backends.ffi import load
from ..backends.generic import *

loaded = load("mouse")

Button: type[GButton] = loaded.Button
# sources:
#lib.backends.standalone.mouse
#lib.backends.x11.mouse
Mouse: type[GMouse] = loaded.Mouse
# sources:
#lib.backends.standalone.mouse
#lib.backends.x11.mouse
