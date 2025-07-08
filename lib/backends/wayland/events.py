from typing import TYPE_CHECKING

from .connection import Connection

if TYPE_CHECKING:
    from ...ctx import Ctx
    from ..generic import GConnection


async def setup(ctx: 'Ctx', task_status):
    conn = Connection()
    ctx.connection = conn

    async def _update():
        await update(ctx, conn)

    # NOTE: conn.fd will only exist if we decide to roll our own event loop
    # ctx.watcher.watch(conn.fd, _update)
    await ctx.nurs.start(conn.run)
    task_status.started()


async def update(ctx: 'Ctx', conn: 'GConnection'):
    print('a')
    # wl.wlEventLoopDispatch
