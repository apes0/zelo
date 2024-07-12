from lib.backends.generic import GWindow
from lib.ctx import Ctx
from ..generic import GMod, GKey


class Mod(GMod):
    def __init__(self, *names: str) -> None:
        self.mod = 0
        self.mods = names


class Key(GKey):
    def __init__(self, lable: str) -> None:
        self.lable = lable
        self.key = 0

    def grab(self, ctx: Ctx, window: GWindow, *modifiers: GMod):
        pass

    def ungrab(self, ctx: Ctx, window: GWindow, *modifiers: GMod):
        pass

    def press(self, ctx: Ctx, window: GWindow, *modifiers: GMod):
        pass

    def release(self, ctx: Ctx, window: GWindow, *modifiers: GMod):
        pass
