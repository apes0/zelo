import subprocess
from typing import TYPE_CHECKING
import os

from .backends.ffi import load

if TYPE_CHECKING:
    from .ctx import Ctx


def spawn(proc: str):
    subprocess.Popen(proc.split(' '), shell=False, env=os.environ.copy())


def stop(ctx: 'Ctx'):
    ctx.closed = True


def close(ctx: 'Ctx', _id: int):
    pass


def changeFocus(ctx: 'Ctx', _id: int):
    ctx.getWindow(_id).setFocus(True)
