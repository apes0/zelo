import subprocess
from typing import TYPE_CHECKING, Any
import os
import trio

from .theme import Theme
from .ratio import Ratio

if TYPE_CHECKING:
    from lib.backends.generic import GWindow, GDisplay
    from lib.ctx import Ctx
    from lib.extension import Extension


def spawn(proc: str):
    subprocess.Popen(proc.split(' '), shell=False, env=os.environ.copy())


def stop(ctx: 'Ctx'):
    ctx.closed = True


async def multiple(*fns):
    async def runner(fn):
        await fn

    async with trio.open_nursery() as nurs:
        for fn in fns:
            nurs.start_soon(runner, fn)


def get(obj: Theme | Ratio | Any, root: 'Extension', field, _type):
    # a function to resolve Ratio / Theme / *
    out = obj
    if isinstance(obj, Theme):
        out = obj.__dict__[field]
    elif isinstance(obj, Ratio):
        if dpy := root.__dict__.get('display'):
            out = obj.getRatio(dpy)
        else:
            out = obj.default(root.ctx)

    if _type:
        out = _type(out)
    return out


def toCursor(ctx: 'Ctx', win: 'GWindow'):
    async def afn():
        x, y = ctx.mouse.location()
        await win.configure(newX=x, newY=y)

    ctx.nurs.start_soon(afn)

def getDisplay(ctx: 'Ctx', x: int, y: int):
    display: 'GDisplay | None' = None

    for _display in ctx.screen.displays:
        if x - _display.x < _display.width and y - _display.y < _display.height:
            display = _display
            break

    return display