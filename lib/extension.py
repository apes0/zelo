import os.path
import pickle
import traceback
from logging import ERROR
from typing import TYPE_CHECKING, Any, Callable, TypeVar, cast

import trio

from utils.fns import get

from .backends.events import Event
from .debcfg import INFO, log

if TYPE_CHECKING:
    from lib.ctx import Ctx

# TODO: export what types of variables can be editted
# FIXME: some extensions cannot be reused for some reason?

dataDir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),  # /lib
    '..',  # /
    'extensions',  # /extensions
    'data',  # /extensions/data
)

fileFmt = '{ext}-{name}.pkl'  # format for file names
# TODO: should we put the file here?


class Extension:
    def __init__(self, ctx: 'Ctx', cfg: dict, resolve={}) -> None:
        self.ctx = ctx
        self.listeners = []
        self.resolve = resolve
        self.loaded = False
        self.unloaded = False
        self.conf(cfg)
        self.loaded = True

    async def __ainit__(self):
        pass

    def conf(self, cfg: dict):
        self.__dict__ = {**self.__dict__, **cfg}

        for lable, _type in self.resolve.items():
            if obj := self.__dict__[lable]:
                self.__dict__[lable] = get(obj, self, lable, _type)

    def addListener(self, event: Event, fn: Callable):
        event.addListener(self.ctx, fn)
        self.listeners.append((event, fn))

    def unload(self):  # ? should this be async?
        if self.unloaded:
            return

        self.unloaded = True
        event: Event
        for event, fn in self.listeners:
            event.removeListener(self.ctx, fn)

        self.unloader()
        # ? anything else here?

    def unloader(self):
        pass  # the way to add custom unloading code

    async def _openFile(self, name: str, mode: str):
        return await trio.open_file(
            os.path.join(
                dataDir, fileFmt.format(ext=self.__class__.__name__, name=name)
            ),
            mode,
        )

    async def loadData(self, name: str) -> object:
        file = await self._openFile(name, 'rb')
        return pickle.loads(await file.read())

    async def saveData(self, name: str, data: object):
        file = await self._openFile(name, 'wb')
        await file.write(pickle.dumps(data))


T = TypeVar('T', bound=Extension)


async def _initExt(ext: type[T], ctx: 'Ctx', cfg: dict, force: bool) -> T:
    log(['backend', 'extensions'], INFO, f'loading {ext} with cfg: {cfg}')
    if not force and (e := ctx.extensions.get(ext)):
        e.conf(cfg)
        return cast(T, e)  # TODO: remove this cast

    e = ext(ctx, cfg)
    async with trio.open_nursery() as nurs:
        nurs.start_soon(e.__ainit__)
    ctx.extensions[ext] = e

    log(['backend', 'extensions'], INFO, f'loaded {ext}')

    return e


async def initExt(ext: type[T], ctx: 'Ctx', cfg: dict, force: bool = False) -> T | None:
    try:
        return await _initExt(ext, ctx, cfg, force)
    except:
        log(
            'extensions',
            ERROR,
            f'{ext} encountered:\n{traceback.format_exc()}',
        )

        return None


async def setupExtensions(ctx: 'Ctx', extensions: dict):
    for extension, cfg in extensions.items():
        # NOTE: here we have a custom wrapper, so we shouldn't use ctx.startSoon
        ctx.nurs.start_soon(initExt, extension, ctx, cfg)


def unloadExtensions(ctx: 'Ctx'):
    for extension in ctx.extensions.values():
        extension.unload()


# TODO: what should the behaviour of function calls here be?
# TODO: i think its a good enoguh idea to just call the function
# TODO: for each instance, but that might not work well
def perDisplay(ext: type[Extension]) -> type[Extension]:
    class New(Extension):
        def __init__(self, ctx: 'Ctx', cfg: dict) -> None:
            for display in ctx.screen.displays:
                ext(ctx, {**cfg, 'display': display})

    return New
