from lib.backends.generic import GKey, GMod, GWindow
from .keysyms import keys
from typing import TYPE_CHECKING
from .. import xcb
from .types import keyEvent
from ..generic import CData

from logging import DEBUG
from ...debcfg import log

if TYPE_CHECKING:
    from ...ctx import Ctx


modMap = {
    'shift': xcb.XCBModMaskShift,
    'lock': xcb.XCBModMaskLock,
    'control': xcb.XCBModMaskControl,
    'alt': xcb.XCBModMask1,
    'numLk': xcb.XCBModMask2,
    'numLock': xcb.XCBModMask2,
    'super': xcb.XCBModMask4,
    'hyper': xcb.XCBModMask4,
    'mod1': xcb.XCBModMask1,
    'mod2': xcb.XCBModMask2,
    'mod3': xcb.XCBModMask3,
    'mod4': xcb.XCBModMask4,
    'mod5': xcb.XCBModMask5,
    'any': xcb.XCBModMaskAny,
    '': 0,  # default, no modifiers
}


class Mod(GMod):
    mappings = {}

    def __init__(self, *names: str, value: int = 0) -> None:
        self.mod = value
        if not value:
            for mod in names:
                self.mod |= modMap[mod]


class Key(GKey):
    cache: dict[str, int] = {
        'any': xcb.XCBGrabAny
    }  # we dont need to get the keycode for this lol (infact it breaks it)
    syms: CData

    def __init__(self, lable: str | None = None, code: int | None = None) -> None:
        assert lable or code, 'You must have the lable or keycode for a key.'
        if lable:
            self.lable = lable.lower()
            self.key: int | None = self.__class__.cache.get(self.lable)
        else:
            self.lable = ''
            self.key = code
            for lable, key in self.__class__.cache.items():
                if key == code:
                    self.lable = lable
                    break

    def load(self, ctx: 'Ctx'):
        syms = self.__class__.syms
        assert syms, 'Couldn\'t allocate key symbols (for some reason)'

        # NOTE: this is adapted from qtile's implementation
        keysym: int | None = keys.get(self.lable)

        assert (
            keysym is not None
        ), f'No {self.lable} key! (you can check keysyms.py for a list of keys)'

        code = xcb.xcbKeySymbolsGetKeycode(syms, keysym)

        assert code, f'Couldn\'t find keycode for {self.lable}...'

        key: int = code[0]
        self.key = key
        self.__class__.cache[self.lable] = key
        # xcb.xcbKeySymbolsFree(syms)  # ? idk how efficient this is lol

    def grab(
        self, ctx: 'Ctx', window: GWindow, *modifiers: Mod
    ):  # TODO: (un)grab on window
        log('grab', DEBUG, f'grabbing {self} with modifiers {modifiers}')
        if self.key is None:
            self.load(ctx)

        mod = 0

        for _mod in modifiers:
            mod |= _mod.mod

        xcb.xcbGrabKey(
            ctx.connection,
            1,
            window.id,
            mod,
            self.key,
            xcb.XCBGrabModeAsync,
            xcb.XCBGrabModeAsync,
        )

        xcb.xcbFlush(ctx.connection)

    def ungrab(self, ctx: 'Ctx', window: GWindow, *modifiers: Mod):
        log('grab', DEBUG, f'ungrabbing {self} with modifiers {modifiers}')
        if self.key is None:
            self.load(ctx)

        mod = 0

        for _mod in modifiers:
            mod |= _mod.mod

        xcb.xcbUngrabKey(ctx.connection, self.key, window.id, mod)
        xcb.xcbFlush(ctx.connection)

    def press(self, ctx: 'Ctx', window: 'GWindow', *modifiers: Mod, flush: bool = True):
        log('press', DEBUG, f'pressing {self} with modifiers {modifiers}')
        if self.key is None:
            self.load(ctx)

        for mod in modifiers:
            i = 1
            while mod.mod:  # break down the summed modifier to the basic modifiers
                if mod.mod % 2:
                    Key(code=Mod.mappings[i][0]).press(ctx, window, flush=False)
                mod.mod = mod.mod >> 1
                i = i << 1

        xcb.xcbTestFakeInput(
            ctx.connection,
            xcb.XCBKeyPress,
            self.key,
            xcb.XCBCurrentTime,
            window.id,
            0,
            0,
            0,
        )

        if flush:
            xcb.xcbFlush(ctx.connection)

    def release(
        self, ctx: 'Ctx', window: 'GWindow', *modifiers: Mod, flush: bool = True
    ):
        log('press', DEBUG, f'releasing {self} with modifiers {modifiers}')
        if self.key is None:
            self.load(ctx)

        for mod in modifiers:
            i = 1
            while mod.mod:  # break down the summed modifier to the basic modifiers
                if mod.mod % 2:
                    Key(code=Mod.mappings[i][0]).release(ctx, window, flush=False)
                mod.mod = mod.mod >> 1
                i = i << 1

        xcb.xcbTestFakeInput(
            ctx.connection,
            xcb.XCBKeyRelease,
            self.key,
            xcb.XCBCurrentTime,
            window.id,
            0,
            0,
            0,
        )

        if flush:
            xcb.xcbFlush(ctx.connection)

    def __hash__(self) -> int:
        return hash(self.lable)
