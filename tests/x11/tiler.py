import random
from ..tester import test
from ..pres import startX, openWins, startWm

from lib._cfg import Cfg
from extensions.tiler import Tiler
from lib.backends.events import focusChange

import trio

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..tester import Test
    from lib.ctx import Ctx

cfg = Cfg()

cfg.focusedColor = 0xaaaaaa
cfg.unfocusedColor = 0x000000

cfg.extensions = {
    Tiler: {
        'mainSize': 2/3,
        'border': 5,
        'spacing': 10,
    },
}

@test('opened == focused?', [startX, startWm(cfg), openWins])
async def OpeningWinsFocusesThem(test: 'Test'):
    ctx: 'Ctx' = test.preq[1].data

    assert ctx.focused != None, 'there must be a focused window'
    

@test('focused == main?', [startX, startWm(cfg), openWins])
async def focusedIsMain(test: 'Test'):
    ctx: 'Ctx' = test.preq[1].data

    assert ctx.focused != None, 'there must be a focused window'
    assert ctx.focused.width == 370, 'The window is not the right size'
    
    unfocused = ctx.windows.copy()
    del unfocused[ctx.focused.id]
    win = random.choice(list(unfocused.values()))

    await win.setFocus(True)
    await trio.sleep(10) # wtf goes on here?????????

    assert ctx.focused != None, 'there must be a focused window'
    assert ctx.focused.width == 370, 'The window is not the right size'
