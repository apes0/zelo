from lib.backends.generic import GWindow
from lib.extension import Extension, single
from typing import TYPE_CHECKING, Callable
from itertools import combinations
from lib.backends.events import keyPress, keyRelease
from lib.api.keys import Mod

if TYPE_CHECKING:
    from lib.backends.generic import GKey, GMod
    from lib.ctx import Ctx


def arun(ctx: 'Ctx', fn: Callable):
    def arunner(*args):
        ctx.nurs.start_soon(fn, *args)

    return arunner


@single
class Shortcuts(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.keys = []
        self.shortcuts: dict = {}
        self._shortcuts: dict = {}

        super().__init__(ctx, cfg)

        baseIgnore: list[str] = [
            'lock',
            'mod2',
        ]  # ? maybe make this a configurable value

        self.baseIgnore: list[GMod] = [Mod(mod) for mod in baseIgnore]
        self.ignore: list[GMod] = [
            *self.baseIgnore,
            Mod(
                '',
            ),
        ]

        for l in range(2, len(baseIgnore) + 1):
            self.ignore += [Mod(*mod) for mod in combinations(baseIgnore, l)]

        self.addListener(keyPress, self.keyPress)
        self.addListener(keyRelease, self.keyRelease)

        self.register()

    def register(self):
        keys = self.shortcuts.keys()
        # NOTE: use xcb.XCB_GRAB_ANY for key to find the keycode
        # keys = [xcb.XCB_GRAB_ANY]

        for (
            _mod
        ) in self.ignore:  # do key.grab for every combination of ignored modifiers
            for key in keys:
                mod: GMod = key[1]  # add the modifier used for the actual shortcut
                for _key in key[0]:
                    _key: GKey
                    _key.grab(self.ctx, _mod, mod)

        shortcuts = {}  # adapt self.shortcuts to the old system, bc lazy

        for (keys, mod), fn in self.shortcuts.items():
            cuts = [key.key for key in keys]
            cuts.sort()
            shortcuts[(tuple(cuts), mod.mod)] = fn

        self._shortcuts = shortcuts

    async def keyPress(self, originalKey: 'GKey', mod: 'GMod', win: 'GWindow'):
        key = originalKey.key  # type: ignore
        for idx, _key in enumerate(self.keys):
            if key == _key:
                break
            if key < _key:
                self.keys.insert(idx, key)
                break
        else:
            self.keys.append(key)
        fn = self._shortcuts.get(
            (tuple(self.keys), mod.mod & ~sum([_mod.mod for _mod in self.baseIgnore]))
        )
        if fn:
            fn(self.ctx)
            self.keys = []

    #        else:
    #            originalKey.press(self.ctx, win, mod)
    #            originalKey.release(self.ctx, win, mod)

    async def keyRelease(self, key: 'GKey', _mod: 'GMod', _win: 'GWindow'):
        key = key.key  # type: ignore
        if key in self.keys:
            self.keys.remove(key)
        else:
            # NOTE: if the key doesn't exist in the list of pressed keys, then it is a modifier, and
            # thus, the keys list should be cleared
            self.keys.clear()

    def conf(self, cfg: dict):
        self.shortcuts = {**self.shortcuts, **cfg['shortcuts']}
