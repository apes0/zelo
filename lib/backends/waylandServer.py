from _cffi_backend import _CDataBase
from wayland_cffi import ffi, lib

from .base import Base, parseArgs

NULL = ffi.NULL

# types

# skipping WlEventLoop, because its not fully defined

# skipping WlDisplay, because its not fully defined

# funcs

wlDisplayAddSocketAuto = lambda *a: (lib.wl_display_add_socket_auto(*parseArgs(a)))
wlDisplayCreate = lambda *a: (lib.wl_display_create(*parseArgs(a)))
wlDisplayDestroy = lambda *a: (lib.wl_display_destroy(*parseArgs(a)))
wlDisplayFlushClients = lambda *a: (lib.wl_display_flush_clients(*parseArgs(a)))
wlDisplayGetEventLoop = lambda *a: (lib.wl_display_get_event_loop(*parseArgs(a)))
wlDisplayRun = lambda *a: (lib.wl_display_run(*parseArgs(a)))
wlEventLoopDispatch = lambda *a: (lib.wl_event_loop_dispatch(*parseArgs(a)))
wlEventLoopGetFd = lambda *a: (lib.wl_event_loop_get_fd(*parseArgs(a)))
