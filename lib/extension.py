from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from lib.ctx import Ctx

# TODO: export what types of variables can be editted


class Extension:
    def __init__(self, ctx: 'Ctx', cfg: dict) -> None:
        self.ctx = ctx
        self.listeners = {}
        self.conf(cfg)

    def conf(self, cfg: dict):
        self.__dict__ = {**self.__dict__, **cfg}

    def addListener(self, event: int, fn: Callable):
        self.listeners[event] = fn

    def assure(self, ext: type) -> 'Extension':
        return self.ctx.extensions.get(ext) or ext(self.ctx, {})


def setupExtensions(ctx: 'Ctx', extensions: dict):
    for extension, cfg in extensions.items():
        if ext := ctx.extensions.get(extension):
            ext.conf(cfg)
            continue
        ctx.extensions[extension] = extension(ctx, cfg)
