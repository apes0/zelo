from ..backends.ffi import load
from..backends.generic import *
loaded = load("drawer")

Image: type[GImage] = loaded.Image
