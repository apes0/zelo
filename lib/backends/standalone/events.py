from typing import TYPE_CHECKING

import pyglet
import pyglet.event
import trio

from .cfg import HEIGHT, WIDTH
from .gctx import Ctx as GCtx

if TYPE_CHECKING:
    from ...ctx import Ctx

window = pyglet.window.Window(
    width=WIDTH,
    height=HEIGHT,
    vsync=False,
    resizable=False,
)

# reference for coords:
# ^ (+)
# |
# |
# |
# |                (+)
# +----------------->
# (0, 0)


async def eloop(ctx: 'Ctx', task_status=trio.TASK_STATUS_IGNORED):
    task_status.started()
    rate = 1 / 60
    while pyglet.app.windows:
        time = trio.current_time()
        pyglet.clock.tick()

        window: pyglet.window.Window
        for window in pyglet.app.windows.copy():
            window.switch_to()
            window.dispatch_events()
            window.dispatch_event('on_draw', ctx)
            window.flip()

        await trio.sleep_until(time + rate)


@window.event
def on_draw(ctx: 'Ctx[GCtx]'):
    for obj in ctx.gctx.toDraw:
        obj.draw()


async def setup(ctx: 'Ctx', task_status=trio.TASK_STATUS_IGNORED):
    gctx = GCtx(ctx)
    ctx.gctx = gctx
    await ctx.nurs.start(eloop, ctx)
    task_status.started()
