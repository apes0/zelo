from typing import Callable, Any
import os
import trio
from lib import watcher
from lib.ctx import Ctx
from lib.backends.ffi import load
from utils.fns import stop
from lib.cfg import cfg
import random

# these are all the prerequesites, they should only block until they can be used


class Pre:
    def __init__(self, lable: str, start: Callable) -> None:
        self.lable: str = lable
        self.start: Callable = start
        self.end: Callable
        self.args: tuple = ()
        self.data: Any

    async def run(self, nurs: trio.Nursery):
        done = trio.Event()
        await self.start(self, nurs, done)
        await done.wait()

    async def stop(self, nurs: trio.Nursery):
        done = trio.Event()
        await self.end(self, nurs, done)
        await done.wait()

    def __call__(self, *args: Any) -> Any:
        self.args = args
        return self


def pre(lable):
    def deco(fn):
        return Pre(lable, fn)

    return deco


def preEnd(pre: Pre):
    def deco(fn):
        pre.end = fn

    return deco


async def popen(nurs: trio.Nursery, proc: str) -> trio.Process:
    async def fn(task_status) -> None:

        async with await trio.open_file(os.devnull) as dn:
            await trio.run_process(
                proc.split(' '),
                task_status=task_status,
                check=False,
                stdout=dn,
                stderr=dn,
            )

    return await nurs.start(fn)


async def pclose(proc: trio.Process):
    proc.terminate()
    with trio.move_on_after(2):
        await proc.wait()
    if proc.poll() == None:
        proc.kill()
        await proc.wait()


@pre('starting X')
async def startX(pre: Pre, nurs: trio.Nursery, done: trio.Event):
    new: str = ':' + str(int(os.environ["DISPLAY"][1:]) + 1)

    proc: trio.Process = await popen(
        nurs, f'Xephyr +extension RANDR +xinerama -ac -br -screen 600x400 {new}'
    )
    pre.data = proc

    await trio.sleep(2)

    assert proc.poll() == None, 'Something went wrong with Xephyr'

    os.environ['DISPLAY'] = new
    done.set()


@preEnd(startX)
async def endX(pre: Pre, nurs: trio.Nursery, done: trio.Event):
    await pclose(pre.data)
    await trio.sleep(1)
    os.environ['DISPLAY'] = ':' + str(int(os.environ["DISPLAY"][1:]) - 1)
    done.set()


@pre('opening Windows')
async def openWins(pre: Pre, nurs: trio.Nursery, done: trio.Event):
    procs: list[trio.Process] = [
        await popen(nurs, random.choice(['xeyes', 'xclock', 'xterm']))
        for i in range(random.randint(3, 10))
    ]
    pre.data = procs

    await trio.sleep(1)

    died: list[int | None] = [procs[0].poll()]
    assert not any(died), 'A proccess died'

    done.set()


@preEnd(openWins)
async def killWins(pre: Pre, nurs: trio.Nursery, done: trio.Event):
    for proc in pre.data:
        await pclose(proc)

    done.set()


@pre('startWm')
async def startWm(pre: Pre, nurs: trio.Nursery, done: trio.Event):
    print(pre.args[0].__dict__)
    cfg.__dict__ = pre.args[0].__dict__.copy()  # new cfg

    async def main(task_status):
        ctx = Ctx()
        pre.data = ctx

        async with trio.open_nursery() as nurs:
            ctx.nurs = nurs
            nurs.start_soon(watcher.setup, ctx)
            nurs.start_soon(load('events').setup, ctx)
            task_status.started()

    await nurs.start(main)
    await trio.sleep(2)
    done.set()


@preEnd(startWm)
async def stopWm(pre: Pre, nurs: trio.Nursery, done: trio.Event):
    stop(pre.data)
    done.set()
