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


def get(obj: Theme | Ratio | float, root: 'Extension', field):
    # a function to resolve Ratio / Theme / *
    if isinstance(obj, Theme):
        return obj.__dict__[field]
    if isinstance(obj, Ratio):
        if dpy := root.__dict__.get('display'):
            return obj.getRatio(dpy)
        else:
            return obj.default(root.ctx)
    else:
        return obj
