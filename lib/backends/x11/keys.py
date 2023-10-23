from lib.backends.generic import GKey, GMod, GWindow
from .keysyms import keys
from typing import TYPE_CHECKING
from xcb_cffi import lib, ffi
from .types import keyEvent, charpC
from ..generic import CData

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
    syms: CData | None = None

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
        if not self.__class__.syms:
            self.__class__.syms = lib.xcb_key_symbols_alloc(ctx.connection)
        syms = self.__class__.syms
        assert syms, 'Couldn\'t allocate key symbols (for some reason)'
        # FIXME: this fails on bigger screen sizes (i tried 1280x720) ((what the fuck is going on lol))
        # NOTE: this is adapted from qtile's implementation
        keysym: int | None = keys.get(self.lable)
        assert (
            keysym
        ), f'No {self.lable} key! (you can check keysyms.py for a list of keys)'
        code = lib.xcb_key_symbols_get_keycode(syms, keysym)
        assert code, f'Couldn\'t find keycode for {self.lable}...'
        self.key = code[0]
        self.__class__.cache[self.lable] = code
        # lib.xcb_key_symbols_free(syms)  # ? idk how efficient this is lol

    def grab(self, ctx: 'Ctx', *modifiers: Mod):
        if not self.key:
            self.load(ctx)

        mod = 0

        for _mod in modifiers:
            mod |= _mod.mod

        lib.xcb_grab_key(
            ctx.connection,
            1,
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

    def press(self, ctx: 'Ctx', window: 'GWindow', *modifiers: Mod):  # TODO: no workie
        if not self.key:
            self.load(ctx)

        mod = 0

        for _mod in modifiers:
            mod |= _mod.mod

        event = keyEvent()
        event.root = ctx._root
        event.event = window.id
        event.child = window.id
        event.response_type = lib.XCB_BUTTON_PRESS
        event.time = lib.XCB_CURRENT_TIME
        event.root_x = 0
        event.root_y = 0
        event.event_x = 0
        event.event_y = 0
        event.state = mod
        event.detail = self.key

        lib.xcb_send_event(
            ctx.connection, 1, window.id, lib.XCB_BUTTON_PRESS, charpC(event)
        )
        lib.xcb_flush(ctx.connection)

    def release(self, ctx: 'Ctx', window: 'GWindow', *modifiers: Mod):
        if not self.key:
            self.load(ctx)

        mod = 0

        for _mod in modifiers:
            mod |= _mod.mod

        event = keyEvent()
        event.root = ctx._root
        event.event = window.id
        event.child = window.id
        event.response_type = lib.XCB_BUTTON_RELEASE
        event.time = lib.XCB_CURRENT_TIME
        event.root_x = 0
        event.root_y = 0
        event.event_x = 0
        event.event_y = 0
        event.state = mod
        event.detail = self.key

        lib.xcb_send_event(
            ctx.connection, 1, window.id, lib.XCB_BUTTON_RELEASE, charpC(event)
        )
        lib.xcb_flush(ctx.connection)

    def __hash__(self) -> int:
        return hash(self.lable)
