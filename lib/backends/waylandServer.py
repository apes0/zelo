from _cffi_backend import _CDataBase
from wayland_cffi import lib, ffi
from typing import Any, Literal
from .base import Base, parseArgs, Ptr, CPtr, void

NULL = ffi.NULL

# types
# skipping WlDisplay, because its not fully defined
class WlDisplay(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
# skipping WlEventLoop, because its not fully defined
class WlEventLoop(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()

# funcs and vars

def wlDisplayAddSocketAuto(display: CPtr[WlDisplay], ) -> Ptr[int]:return Ptr(lib.wl_display_add_socket_auto(*parseArgs(display, )))
def wlDisplayCreate() -> CPtr[WlDisplay]:return WlDisplay(lib.wl_display_create(*parseArgs()))
def wlDisplayDestroy(display: CPtr[WlDisplay], ) -> void:return void(lib.wl_display_destroy(*parseArgs(display, )))
def wlDisplayFlushClients(display: CPtr[WlDisplay], ) -> void:return void(lib.wl_display_flush_clients(*parseArgs(display, )))
def wlDisplayGetEventLoop(display: CPtr[WlDisplay], ) -> CPtr[WlEventLoop]:return WlEventLoop(lib.wl_display_get_event_loop(*parseArgs(display, )))
def wlDisplayRun(display: CPtr[WlDisplay], ) -> void:return void(lib.wl_display_run(*parseArgs(display, )))
def wlEventLoopDispatch(loop: CPtr[WlEventLoop], timeout: int, ) -> int:return int(lib.wl_event_loop_dispatch(*parseArgs(loop, timeout, )))
def wlEventLoopGetFd(loop: CPtr[WlEventLoop], ) -> int:return int(lib.wl_event_loop_get_fd(*parseArgs(loop, )))
