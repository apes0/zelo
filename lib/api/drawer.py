from ..backends.ffi import load
from ..backends.generic import *

loaded = load("drawer")

Image: type[GImage] = loaded.Image
# sources:
#lib.backends.standalone.drawer
#lib.backends.wayland.drawer
#lib.backends.x11.drawer
Rectangle: type[GRectangle] = loaded.Rectangle
# sources:
#lib.backends.standalone.drawer
#lib.backends.wayland.drawer
#lib.backends.x11.drawer
Text: type[GText] = loaded.Text
# sources:
#lib.backends.standalone.drawer
#lib.backends.wayland.drawer
#lib.backends.x11.drawer
