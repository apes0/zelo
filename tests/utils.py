from typing import TYPE_CHECKING
import random
import trio
import os

if TYPE_CHECKING:
    from lib.backends.generic import GWindow
    from lib.ctx import Ctx


def checkWin(
    win: 'GWindow', x: int | None, y: int | None, w: int | None, h: int | None
):
    return (
        (win.x == x) * bool(x)
        and (win.y == y) * bool(y)
        and (win.width == w) * bool(y)
        and (win.height == h) * bool(h)
    )


async def randFocus(ctx: 'Ctx'):
    wins = [win for win in ctx.windows.values() if ctx.editable(win)]

    assert wins, 'no windows to focus'

    win = random.choice(wins)

    await win.setFocus(True)
    await trio.sleep(2)

    return win


async def popen(nurs: trio.Nursery, cmd: str, env: dict | None = None) -> trio.Process:
    dn = await trio.open_file(os.devnull)

    async def fn(task_status):
        try:
            await trio.run_process(
                cmd.split(' '),
                task_status=task_status,
                check=False,
                stdout=dn,  # thank fuck for these
                stderr=dn,  # thank fuck for these
                env=env,
            )
        except BaseException:
            return

    proc: trio.Process = await nurs.start(fn)

    await dn.aclose()

    return proc


async def pclose(proc: trio.Process):
    if proc.poll() is not None:
        return

    proc.terminate()
    with trio.move_on_after(2):
        await proc.wait()
    if proc.poll() == None:
        proc.kill()
        await proc.wait()
