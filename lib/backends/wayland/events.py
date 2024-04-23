from lib.watcher import watch
from .connection import Connection

from .. import waylandServer as wl

from typing import TYPE_CHECKING

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
    watch(conn.fd, _update)


async def update(ctx: 'Ctx', conn: 'GConnection'):
    print('a')
    wl.wlEventLoopDispatch
