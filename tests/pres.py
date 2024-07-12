from typing import Callable, Any
import os
import trio
from lib.ctx import Ctx
from lib.lock import alock
from .ctx import Ctx as TCtx
from lib.backends.x11.types import chararr
from lib.backends.ffi import load
from utils.fns import stop
from lib._cfg import Cfg
import random
from .utils import popen, pclose

# these are all the prerequesites, they should only block until they can be used


class Pre:
    def __init__(self, lable: str, start: Callable) -> None:
        self.lable: str = lable
        self.start: Callable = start
        self.end: Callable
        self.args: tuple = ()
        self.data: Any

    async def run(self, ctx: TCtx):
        done = trio.Event()
        await self.start(self, ctx, done)
        await done.wait()

    async def stop(self, ctx: TCtx):
        done = trio.Event()
        await self.end(self, ctx, done)
        await done.wait()

    def __call__(self, *args: Any) -> Any:
        new = Pre(self.lable, self.start)
        new.end = self.end
        new.args = args or self.args
        return new


def pre(lable):
    def deco(fn):
        return Pre(lable, fn)

    return deco


def preEnd(pre: Pre):
    def deco(fn):
        pre.end = fn

    return deco


@pre('X11')
@alock
async def startX(pre: Pre, ctx: TCtx, done: trio.Event):
    i = int(ctx.env['DISPLAY'][1:])
    xdir = os.listdir('/tmp/.X11-unix')

    while True:
        if f'X{i}' not in xdir:
            new = f':{i}'
            break
        i += 1

    proc: trio.Process = await popen(
        ctx.nurs, f'Xephyr +extension RANDR +xinerama -ac -br -screen 600x400 {new}'
    )
    pre.data = proc

    for _ in range(20):
        await trio.sleep(0.1)  # i think xrefresh makes a lock????
        p = await popen(ctx.nurs, f'xrefresh -d {new}')
        if await p.wait():
            await pclose(p)
            break

        await pclose(p)

    assert (
        proc.poll() == None
    ), f'Something went wrong with Xephyr (returned {proc.poll()} on display {i})'

    ctx.env['DISPLAY'] = new
    done.set()


@preEnd(startX)
async def endX(pre: Pre, ctx: TCtx, done: trio.Event):
    await pclose(pre.data)
    for _ in range(20):
        p = await popen(ctx.nurs, f'xrefresh', ctx.env)
        if await p.wait():
            await pclose(p)
            break

        await pclose(p)
        await trio.sleep(0.1)
    done.set()


@pre('Windows')
async def openWins(pre: Pre, ctx: TCtx, done: trio.Event):
    procs: list[trio.Process] = [
        await popen(
            ctx.nurs,
            random.choice(['xclock', 'xterm', 'xedit', 'xbiff', 'xlogo']),
            ctx.env,
        )
        # oclock and xeyes remove borders :P
        # xman fails on the automated tests bc no man pages
        for _ in range(random.randint(3, 10))
    ]

    pre.data = procs

    await trio.sleep(1)

    died: list[int | None] = [proc.poll() for proc in procs]
    assert not any(died), f'A proccess died (return codes are: {died})'

    done.set()


@preEnd(openWins)
async def killWins(pre: Pre, ctx: TCtx, done: trio.Event):
    for proc in pre.data:
        await pclose(proc)

    done.set()


@pre('Wm')
@alock
async def startWm(pre: Pre, tctx: TCtx, done: trio.Event):
    async def main(task_status):
        ctx = Ctx()
        pre.data = ctx
        cfg = Cfg()
        cfg.__dict__ = pre.args[0].__dict__.copy()
        ctx.cfg = cfg

        async with trio.open_nursery() as nurs:
            ctx.nurs = nurs
            ctx.gctxConf['display'] = tctx.env['DISPLAY'].encode()
            await nurs.start(load('events').setup, ctx)
            await nurs.start(ctx.watcher.start, ctx)
            task_status.started()

    await tctx.nurs.start(main)
    done.set()


@preEnd(startWm)
async def stopWm(pre: Pre, ctx: TCtx, done: trio.Event):
    await stop(pre.data)
    done.set()
