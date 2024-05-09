from ..utils import checkWin, randFocus
from ..tester import Shared, test
from ..pres import startX, openWins, startWm

from lib._cfg import Cfg
from extensions.tiler import Tiler

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
}

defShared = Shared([startX, startWm(cfg), openWins])

@defShared
@test('opened == focused?', [])
async def OpeningWinsFocusesThem(test: 'Test'):
    ctx: 'Ctx' = test.pres[0].data[1]

    await randFocus(ctx)

    assert ctx.focused != None, 'there must be a focused window'


@defShared
@test('focused == main?', [])
async def focusedIsMain(test: 'Test'):
    ctx: 'Ctx' = test.pres[0].data[1]

    assert ctx.focused != None, 'there must be a focused window'
    assert checkWin(ctx.focused, 10, 10, 370, 370), 'The window is not the right size'

    win = await randFocus(ctx)

    assert ctx.focused.id == win.id, 'setFocus doesn\'t work'
    assert checkWin(ctx.focused, 10, 10, 370, 370), 'The window is not the right size'

@defShared
@test('are side windows correct?', [])
async def checkSideWins(test: 'Test'):
    ctx: 'Ctx' = test.pres[0].data[1]

    await randFocus(ctx)

    for win in ctx.windows.values():
        if not win.focused:
            # TODO: check more here
            assert win.x == 400, 'Side window has a wrong size'

bigBorders = Cfg()

bigBorders.focusedColor = cfg.focusedColor
bigBorders.unfocusedColor = cfg.unfocusedColor

border = 20

bigBorders.extensions = {
    Tiler: {
        'mainSize': 2/3,
        'border': border,
        'spacing': 5
    }
}

bigShared = Shared([startX, startWm(bigBorders), openWins])

@bigShared
@test('border size works?', [])
async def bigBorder(test: 'Test'):
    ctx: 'Ctx' = test.pres[0].data[1]

    await randFocus(ctx)

    for win in ctx.windows.values():
        assert win.borderWidth == border, 'Border size is incorrect'

bigSpacing = Cfg()

bigSpacing.focusedColor = cfg.focusedColor
bigSpacing.unfocusedColor = cfg.unfocusedColor

spacing = 20

bigSpacing.extensions = {
    Tiler: {
        'mainSize': 2/3,
        'border': 5,
        'spacing': spacing
    }
}

# TODO: check big spacing