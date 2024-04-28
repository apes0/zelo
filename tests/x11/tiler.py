import random

from extensions.winfo import Winfo
from ..tester import Shared, test
from ..pres import startX, openWins, startWm

from lib._cfg import Cfg
from extensions.tiler import Tiler

import trio

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..tester import Test
    from lib.ctx import Ctx

cfg = Cfg()

cfg.focusedColor = 0xaaaaaa
cfg.unfocusedColor = 0x444444

cfg.extensions = {
    Tiler: {
        'mainSize': 2 / 3,
        'border': 5,
        'spacing': 10,
    },
#    Winfo: {}
}

shared = Shared([startX, startWm(cfg), openWins])

@shared
@test('opened == focused?', [])
async def OpeningWinsFocusesThem(test: 'Test'):
    ctx: 'Ctx' = test.pres[0].data[1]

    assert ctx.focused != None, 'there must be a focused window'


@shared
@test('focused == main?', [])
async def focusedIsMain(test: 'Test'):
    ctx: 'Ctx' = test.pres[0].data[1]

    assert ctx.focused != None, 'there must be a focused window'
    assert ctx.focused.height == 370, 'The window is not the right size'

    unfocused = ctx.windows.copy()
    del unfocused[ctx.focused.id]
    win = random.choice(list(unfocused.values()))

    await win.setFocus(True)
    await trio.sleep(2)

    assert ctx.focused.id == win.id, 'setFocus doesn\'t work'
    assert ctx.focused.height == 370, 'The window is not the right size'

# TODO: check if all side windows are the correct size
# TODO: check if all config vars work