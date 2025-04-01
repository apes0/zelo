from collections import deque
from typing import (TYPE_CHECKING, Any, Callable, Concatenate, ParamSpec,
                    TypeVar)

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
            while self.queue:
                # print(f'{len(self.queue)} pending requests')
                r: Request = self.queue.popleft()
                # print(f'handling {r}')
                r.data = r.respf(self.ctx._getGCtx().connection, r.req, xcb.NULL)
                trio.from_thread.run_sync(r.finished.set)

            self._start = trio.Event()
            trio.from_thread.run(self._start.wait)

    def add(self, req: Request):
        self.queue.append(req)
        self._start.set()


GetScreenResources = _Request(
    xcb.xcbRandrGetScreenResources, xcb.xcbRandrGetScreenResourcesReply
)
RandrGetCrtcInfo = _Request(xcb.xcbRandrGetCrtcInfo, xcb.xcbRandrGetCrtcInfoReply)
GetProperty = _Request(xcb.xcbGetProperty, xcb.xcbGetPropertyReply)
QueryTree = _Request(xcb.xcbQueryTree, xcb.xcbQueryTreeReply)
GetWindowAttributes = _Request(
    xcb.xcbGetWindowAttributes, xcb.xcbGetWindowAttributesReply
)
GetGeometry = _Request(xcb.xcbGetGeometry, xcb.xcbGetGeometryReply)
GetModifierMapping = _Request(
    xcb.xcbGetModifierMappingUnchecked, xcb.xcbGetModifierMappingReply
)
QueryExtension = _Request(xcb.xcbQueryExtensionUnchecked, xcb.xcbQueryExtensionReply)
ShmQueryVersion = _Request(xcb.xcbShmQueryVersion, xcb.xcbShmQueryVersionReply)
QueryPointer = _Request(xcb.xcbQueryPointer, xcb.xcbQueryPointerReply)
ShmGetImage = _Request(xcb.xcbShmGetImageUnchecked, xcb.xcbShmGetImageReply)
GetImage = _Request(xcb.xcbGetImage, xcb.xcbGetImageReply)
