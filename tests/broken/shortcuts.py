import random
from string import ascii_lowercase
from typing import TYPE_CHECKING

import trio

from extensions.shortcuts import Shortcuts
from lib._cfg import Cfg
from lib.api.keys import Key, Mod

from ..pres import openWins, startWm, startX
from ..tester import Shared, test

if TYPE_CHECKING:
    from lib.ctx import Ctx

    from ..tester import Test

cfg = Cfg()

cfg.extensions = {Shortcuts: {}}

defShared = Shared([startX, startWm(cfg), openWins])


# @defShared
# @test('shortcut buttons work?', [])
async def shortcutKeys(test: 'Test'):
    ctx: Ctx = test.pres[0].data[1]

    ev = trio.Event()
    random.choice
    keys = [
        Key(key)
        for key in set(
            random.choices(ascii_lowercase, k=random.randint(0, len(ascii_lowercase)))
        )
    ]
    cuts = Shortcuts(ctx, {'shortcuts': {}})  # type: ignore
    cuts.shortcuts = {(tuple(keys), Mod('any')): lambda ctx: ev.set()}  # reset it
    cuts.register()

    for key in keys:
        key.press(ctx, ctx.root)
        await trio.sleep(0.1)

    await trio.sleep(0.1)
    await ev.wait()

    for key in keys:
        key.release(ctx, ctx.root)
        await trio.sleep(0.1)


mods = [
    'shift',
    'control',
    'alt',
    'super',
    'hyper',
    'mod1',
    'mod2',
    'mod3',
    'mod4',
    'mod5',
]


@defShared
@test('shortcut mods work?', [])
async def shortcutMods(test: 'Test'):
    ctx: Ctx = test.pres[0].data[1]

    ev = trio.Event()
    key = Key(random.choice(ascii_lowercase))

    cuts = Shortcuts(ctx, {'shortcuts': {}})  # type: ignore

    _mods = [mod for mod in set(random.choices(mods, k=random.randint(0, len(mods))))]
    _mod = Mod(*_mods)

    cuts.shortcuts = {((key,), _mod): lambda ctx: ev.set()}  # reset it
    cuts.register()

    key.press(ctx, ctx.root, _mod)

    await ev.wait()

    key.release(ctx, ctx.root, _mod)

    await trio.sleep(0.1)
    cuts.unload()
