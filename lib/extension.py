from logging import ERROR

from .backends.events import Event
from .debcfg import log
import traceback
from typing import TYPE_CHECKING, Any, Callable
import pickle
import trio
import os.path

from utils.fns import get

if TYPE_CHECKING:
    from lib.ctx import Ctx

# TODO: export what types of variables can be editted
# FIXME: some extensions cannot be reused for some reason?

dataDir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), # /lib
    '..', # /
    'extensions', # /extensions
    'data' # /extensions/data
)

fileFmt = '{ext}-{name}.pkl' # format for file names
# TODO: should we put the file here?

class Extension:
    def __init__(self, ctx: 'Ctx', cfg: dict, resolve={}) -> None:
        self.ctx = ctx
        self.listeners = []
        self.resolve = resolve
        self.unloaded = False
        self.conf(cfg)

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
        return await trio.open_file(os.path.join(dataDir, fileFmt.format(ext=self.__class__.__name__, name=name)), mode)

    async def loadData(self, name: str) -> object:
        file = await self._openFile(name, 'rb')
        return pickle.loads(await file.read())

    async def saveData(self, name: str, data: object):
        file = await self._openFile(name, 'wb')
        await file.write(pickle.dumps(data))


def setupExtensions(ctx: 'Ctx', extensions: dict):
    for extension, cfg in extensions.items():
        try:
            if ext := ctx.extensions.get(extension):
                ext.conf(cfg)
                continue
            ctx.extensions[extension] = extension(ctx, cfg)
        except:
            log('extensions', ERROR, traceback.format_exc())


def unloadExtensions(ctx: 'Ctx'):
    for extension in ctx.extensions.values():
        extension.unload()


def single(ext: type[Extension]) -> Extension:
    # TODO: make this be single for the ctx
    class New(Extension):
        def __init__(self) -> None:
            self.ext = None

        def __call__(self, ctx: 'Ctx', conf: dict) -> Any:  # fake init function lol
            if not self.ext:
                self.ext = ext(ctx, conf)
            self.ext.conf(conf)
            return self.ext

    return New()


# TODO: what should the behaviour of function calls here be?
# TODO: i think its a good enoguh idea to just call the function
# TODO: for each instance, but that might not work well
def perDisplay(ext: type[Extension]) -> Extension:
    class New(Extension):
        def __init__(self, ctx: 'Ctx', cfg: dict) -> None:
            for display in ctx.screen.displays:
                ext(ctx, {**cfg, 'display': display})

    return single(New)
