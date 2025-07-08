from .. import waylandServer as wl
from ..generic import GConnection
from ...debcfg import log, DEBUG
import trio

import os


class Connection(GConnection):
    def __init__(self) -> None:
        self.dpy = wl.wlDisplayCreate()

        # NOTE: i should probabbly follow more of this spec, but this is enough to not get a NULL from wl.wlDisplayAddSocketAuto
        # https://specifications.freedesktop.org/basedir-spec/latest/
        os.environ['XDG_RUNTIME_DIR'] = '/tmp'

        self.sock = wl.wlDisplayAddSocketAuto(self.dpy)
        self.eventLoop = wl.wlDisplayGetEventLoop(self.dpy)
        # TODO: do we want to use our own trio event loop?
        # self.fd = wl.wlEventLoopGetFd(self.eventLoop)

        out = b''

        for c in self.sock:
            if c == b'\x00':
                break

            # TODO: fix typing for chars
            out += c

        self.display = out.decode()

    def _run(self, started):
        log('backend', DEBUG, f'running on {self.display}')
        trio.from_thread.run_sync(started)  # task_status.started
        wl.wlDisplayRun(self.dpy)

    async def run(self, task_status=trio.TASK_STATUS_IGNORED):
        # this is the exact same mechanism as in lib/watcher.py
        await trio.to_thread.run_sync(self._run, task_status.started)

    def disconnect(self):
        wl.wlDisplayDestroy(self.dpy)
