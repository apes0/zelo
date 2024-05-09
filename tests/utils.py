from typing import TYPE_CHECKING
import random
import trio
import os

if TYPE_CHECKING:
    from lib.backends.generic import GWindow


def checkWin(win: 'GWindow', x: int, y: int, w: int, h: int):
    return win.x == x and win.y == y and win.width == w and win.height == h

async def randFocus(ctx):
    unfocused = ctx.windows.copy()
    assert unfocused, 'no windows to focus'

    if ctx.focused and ctx.focused.id in unfocused:
        del unfocused[ctx.focused.id]

    win = random.choice(list(unfocused.values()))

    await win.setFocus(True)
    await trio.sleep(2)

    return win

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