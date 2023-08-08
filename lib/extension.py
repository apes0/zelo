from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from lib.ctx import Ctx

# TODO: export what types of variables can be editted
# TODO: configuring plugins by name in cfg.py?

class Extension:
    def __init__(self, name: str) -> None:
        self.ctx: 'Ctx'
        self.name = name
        self.listeners = {}
    
    def addListener(self, event: int, fn: Callable):
        self.listeners[event] = fn
