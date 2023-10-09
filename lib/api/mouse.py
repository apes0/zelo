from ..backends.ffi import load
from..backends.generic import *
loaded = load("mouse")

Button: type[GButton] = loaded.Button
