from typing import TYPE_CHECKING

from .. import waylandServer as wl
from .connection import Connection

if TYPE_CHECKING:
    from ...ctx import Ctx
    from ..generic import GConnection


async def setup(ctx: 'Ctx'):
    conn = Connection()
    print('i came')
    ctx.connection = conn.conn

    async def _update():
        await update(ctx, conn)

    a = wl.wlEventLoopDispatch(conn.eventLoop, 0)
    print(a)
    ctx.watcher.watch(conn.fd, _update)


async def update(ctx: 'Ctx', conn: 'GConnection'):
    print('a')
    wl.wlEventLoopDispatch
