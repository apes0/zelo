from collections import deque
from typing import Callable, TYPE_CHECKING, Concatenate, TypeVar, Any, ParamSpec
import trio
from .. import xcb

if TYPE_CHECKING:
    from ...ctx import Ctx

Ret = TypeVar('Ret')


class Request[Ret]:
    def __init__(self, req, respf: Callable[..., Ret]) -> None:
        self.req = req
        self.respf = respf

        self.finished = trio.Event()
        self.data: Ret

    async def reply(self) -> Ret:
        await self.finished.wait()
        print(self.data)
        return self.data


Args = ParamSpec('Args')


def _Request(
    reqf: Callable[Args, Any], respf: Callable[..., Ret]
) -> Callable[Concatenate['Ctx', Args], Request[Ret]]:
    def makeReq(ctx: 'Ctx', *a, **kwa):
        req = Request(reqf(*a, **kwa), respf)
        ctx._getGCtx().requestLoop.add(req)
        return req

    return makeReq


class RequestLoop:

    def __init__(self, ctx: 'Ctx') -> None:
        self.queue = deque()
        self._start = trio.Event()
        self.ctx = ctx

    async def start(self, task_status=trio.TASK_STATUS_IGNORED):
        await trio.to_thread.run_sync(self.loop, task_status.started)

    def loop(self, fin: Callable):
        trio.from_thread.run_sync(fin)
        while not self.ctx.closed:
            print(f'{len(self.queue)} pending requests')
            while self.queue:
                r: Request = self.queue.popleft()
                print(f'handling {r}')
                r.data = r.respf(self.ctx._getGCtx().connection, r.req, xcb.NULL)
                trio.from_thread.run_sync(r.finished.set)

            self._start = trio.Event()
            trio.from_thread.run(self._start.wait)

    def add(self, req: Request):
        self.queue.append(req)
        self._start.set()


ScreenRes = _Request(
    xcb.xcbRandrGetScreenResources, xcb.xcbRandrGetScreenResourcesReply
)
