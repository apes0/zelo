from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from lib.ctx import Ctx

# TODO: export what types of variables can be editted


class Extension:
    def __init__(self, ctx: 'Ctx', cfg: dict) -> None:
        self.ctx = ctx
        self.listeners = {}
        self.__dict__ = {**self.__dict__, **cfg}

    def addListener(self, event: int, fn: Callable):
        self.listeners[event] = fn
