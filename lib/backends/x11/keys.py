from typing import TYPE_CHECKING

from lib.backends.generic import GKey, GMod, GWindow, applyPre

from .. import xcb
from .keysyms import keys

if TYPE_CHECKING:
    from .gctx import Ctx as GCtx
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


@applyPre
class Mod(GMod):
    mappings = {}

    def __init__(self, *names: str, value: int = 0) -> None:
        self.mod = value
        if not value:
            for mod in names:
                self.mod |= modMap[mod]


@applyPre
class Key(GKey):
    cache: dict[str, int] = {
        'any': xcb.XCBGrabAny
    }  # we dont need to get the keycode for this lol (infact it breaks it)

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

    def load(self, ctx: 'Ctx[GCtx]'):
        syms = xcb.xcbKeySymbolsAlloc(ctx.gctx.connection)
        assert syms, "Couldn't allocate key symbols (for some reason)"

        # NOTE: this is adapted from qtile's implementation
        keysym: int | None = keys.get(self.lable)

        assert keysym is not None, (
            f'No {self.lable} key! (you can check keysyms.py for a list of keys)'
        )

        code = xcb.xcbKeySymbolsGetKeycode(syms, keysym)

        assert code, f"Couldn't find keycode for {self.lable}..."

        key: int = code[0]
        self.key = key
        self.__class__.cache[self.lable] = key
        xcb.xcbKeySymbolsFree(syms)

    def grab(
        self, ctx: 'Ctx[GCtx]', window: GWindow, *modifiers: Mod
    ):  # TODO: (un)grab on window
        assert not ctx.closed, 'conn is closed'

        if self.key is None:
            self.load(ctx)

        mod = 0

        for _mod in modifiers:
            mod |= _mod.mod

        xcb.xcbGrabKey(
            ctx.gctx.connection,
            1,
            window.id,
            mod,
            self.key,
            xcb.XCBGrabModeAsync,
            xcb.XCBGrabModeAsync,
        )

        xcb.xcbFlush(ctx.gctx.connection)

    def ungrab(self, ctx: 'Ctx[GCtx]', window: GWindow, *modifiers: Mod):
        assert not ctx.closed, 'conn is closed'

        if self.key is None:
            self.load(ctx)

        mod = 0

        for _mod in modifiers:
            mod |= _mod.mod

        xcb.xcbUngrabKey(ctx.gctx.connection, self.key, window.id, mod)
        xcb.xcbFlush(ctx.gctx.connection)

    def press(self, ctx: 'Ctx[GCtx]', window: 'GWindow', *modifiers: Mod):
        assert not ctx.closed, 'conn is closed'

        if self.key is None:
            self.load(ctx)

        # TODO: handle mods properly
        xcb.xcbTestFakeInput(
            ctx.gctx.connection,
            xcb.XCBKeyPress,
            self.key,
            xcb.XCBCurrentTime,
            window.id,
            0,
            0,
            0,
        )
        xcb.xcbTestFakeInput(
            ctx.gctx.connection,
            xcb.XCBKeyRelease,
            self.key,
            xcb.XCBCurrentTime,
            window.id,
            0,
            0,
            0,
        )

    def __hash__(self) -> int:
        return hash(self.lable)
