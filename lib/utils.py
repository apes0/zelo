import subprocess
from typing import TYPE_CHECKING
import os
import trio


from .backends.ffi import load

if TYPE_CHECKING:
    from lib.extension import Extension
    from lib.backends.generic import GDisplay
    from .ctx import Ctx


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


class Theme:
    def __init__(self, fore: int, back: int) -> None:
        self.fore = fore
        self.back = back


class Ratio:
    def __init__(
        self, ratio: float, width: bool | None = None, height: bool | None = None
    ) -> None:
        self.ratio = ratio
        self.width = True if width is None else width
        self.height = True if height is None else height

    def getRatio(self, display: 'GDisplay'):
        # TODO: is this a good idea?
        return (
            self.ratio
            * (display.width * self.width + display.height * self.height)
            / (self.width + self.height)
        )

    def default(self, ctx: 'Ctx'):
        return sum([self.getRatio(dpy) for dpy in ctx.screen.displays]) / len(
            ctx.screen.displays
        )


def get(obj: Theme | Ratio | float, root: 'Extension', field, _type):
    # a function to resolve Ratio / Theme / *
    out = obj
    if isinstance(obj, Theme):
        out = obj.__dict__[field]
    elif isinstance(obj, Ratio):
        if dpy := root.__dict__.get('display'):
            out = obj.getRatio(dpy)
        else:
            out = obj.default(root.ctx)

    return _type(out)
