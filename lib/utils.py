import subprocess
from typing import TYPE_CHECKING

from .ffi import lib as xcb

if TYPE_CHECKING:
    from .ctx import Ctx


def spawn(proc: str):
    subprocess.Popen(proc.split(' '), shell=False)


def stop(ctx: 'Ctx'):
    xcb.xcb_disconnect(ctx.connection)
