from .. import waylandServer as wl
from ..generic import GConnection


class Connection(GConnection):
    def __init__(self) -> None:
        self.dpy = wl.wlDisplayCreate()

        self.sock = wl.wlDisplayAddSocketAuto(self.dpy)[0]
        self.eventLoop = wl.wlDisplayGetEventLoop(self.dpy)
        self.fd = wl.wlEventLoopGetFd(self.eventLoop)

        wl.wlDisplayRun(self.dpy)

        wl.wlDisplayDestroy(self.dpy)
