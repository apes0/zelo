from ..backends.ffi import load
from ..backends.generic import *

loaded = load("drawer")

Image: type[GImage] = loaded.Image
Rectangle: type[GRectangle] = loaded.Rectangle
Text: type[GText] = loaded.Text
