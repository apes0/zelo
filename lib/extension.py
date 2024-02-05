import traceback
from typing import TYPE_CHECKING, Any, Callable
from lib.utils import get
import logging

if TYPE_CHECKING:
    from lib.ctx import Ctx

# TODO: export what types of variables can be editted


class Extension:
    def __init__(self, ctx: 'Ctx', cfg: dict, resolve=[]) -> None:
        self.ctx = ctx
        self.listeners = {}
        self.resolve = resolve
        self.conf(cfg)

    def conf(self, cfg: dict):
        self.__dict__ = {**self.__dict__, **cfg}

        for lable in self.resolve:
            if obj := self.__dict__[lable]:
                self.__dict__[lable] = get(obj, self, field=lable)

    def addListener(self, event: int, fn: Callable):
        self.listeners[event] = fn


def setupExtensions(ctx: 'Ctx', extensions: dict):
    for extension, cfg in extensions.items():
        try:
            if ext := ctx.extensions.get(extension):
                ext.conf(cfg)
                continue
            ctx.extensions[extension] = extension(ctx, cfg)
        except:
            logging.error(traceback.format_exc())


def single(ext: type[Extension]) -> Extension:
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
