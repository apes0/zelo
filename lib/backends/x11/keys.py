from lib.backends.generic import GKey, GMod
from .keysyms import keys
from typing import TYPE_CHECKING
from xcb_cffi import lib, ffi

if TYPE_CHECKING:
    from ...ctx import Ctx


modMap = {
    'shift': lib.XCB_MOD_MASK_SHIFT,
    'lock': lib.XCB_MOD_MASK_LOCK,
    'control': lib.XCB_MOD_MASK_CONTROL,
    'mod1': lib.XCB_MOD_MASK_1,
    'mod2': lib.XCB_MOD_MASK_2,
    'mod3': lib.XCB_MOD_MASK_3,
    'mod4': lib.XCB_MOD_MASK_4,
    'mod5': lib.XCB_MOD_MASK_5,
    'any': lib.XCB_MOD_MASK_ANY,
    '': 0,  # default, no modifiers
}


class Mod(GMod):
    def __init__(self, *names: str, value: int = 0) -> None:
        self.mod = value
        if not value:
            for mod in names:
                self.mod |= modMap[mod]


class Key(GKey):
    cache: dict[str, int] = {}

    def __init__(self, lable: str | None = None, code: int | None = None) -> None:
        assert lable or code, 'You must have the lable or keycode for a key.'
        if lable:
            self.lable = lable.lower()
            self.key: int | None = self.__class__.cache.get(lable)
        else:
            self.key = code
            for lable, key in self.__class__.cache.items():
                if key == code:
                    self.lable = lable
                    break

    def load(self, ctx: 'Ctx'):
        # FIXME: this fails on bigger screen sizes (i tried 1280x720)
        # NOTE: this is adapted from qtile's implementation
        keysym: int | None = keys.get(self.lable)
        assert (
            keysym
        ), f'No {self.lable} key! (you can check keysyms.py for a list of keys)'
        syms = lib.xcb_key_symbols_alloc(ctx.connection)
        code = lib.xcb_key_symbols_get_keycode(syms, keysym)
        if code != ffi.NULL:
            code = code[0]
        else:
            code = 0
        assert code, f'Couldn\'t find keycode for {self.lable}...'
        lib.xcb_key_symbols_free(syms)  # ? idk how efficient this is lol
        self.key = code
        self.__class__.cache[self.lable] = code

    def grab(self, ctx: 'Ctx', *modifiers: Mod):
        if not self.key:
            self.load(ctx)

        mod = 0

        for _mod in modifiers:
            mod |= _mod.mod

        lib.xcb_grab_key(
            ctx.connection,
            0,
            ctx._root,
            mod,
            self.key,
            lib.XCB_GRAB_MODE_ASYNC,
            lib.XCB_GRAB_MODE_ASYNC,
        )

        lib.xcb_flush(ctx.connection)

    def ungrab(self, ctx: 'Ctx', *modifiers: Mod):
        if not self.key:
            self.load(ctx)

        mod = 0

        for _mod in modifiers:
            mod |= _mod.mod

        lib.xcb_ungrab_key(ctx.connection, self.key, ctx._root, mod)
        lib.xcb_flush(ctx.connection)

    def __hash__(self) -> int:
        return hash(self.lable)
