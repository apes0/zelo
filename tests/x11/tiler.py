from ..utils import checkWin, randFocus
from ..tester import test
from ..pres import startX, openWins, startWm

from lib._cfg import Cfg
from extensions.tiler import Tiler

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.ctx import Ctx
    from ..ctx import Ctx as TCtx

cfg = Cfg()

cfg.extensions = {
    Tiler: {
        'mainSize': 2 / 3,
        'border': 5,
        'spacing': 10,
    },
}

suit = 'x11/tiler'


@test('opened == focused?', [startX, startWm(cfg), openWins], suit)
async def OpeningWinsFocusesThem(tctx: 'TCtx'):
    ctx: 'Ctx' = tctx.pres[1].data

    await randFocus(ctx)

    assert ctx.focused != None, 'there must be a focused window'


@test('focused == main?', [startX, startWm(cfg), openWins], suit)
async def focusedIsMain(tctx: 'TCtx'):
    ctx: 'Ctx' = tctx.pres[1].data

    assert ctx.focused != None, 'there must be a focused window'
    assert checkWin(ctx.focused, 10, 10, 378, 378), 'The window is not the right size'

    win = await randFocus(ctx)

    assert ctx.focused.id == win.id, 'setFocus doesn\'t work'
    assert checkWin(ctx.focused, 10, 10, 378, 378), 'The window is not the right size'


@test('side windows correct?', [startX, startWm(cfg), openWins], suit)
async def checkSideWins(tctx: 'TCtx'):
    ctx: 'Ctx' = tctx.pres[1].data

    await randFocus(ctx)

    for win in ctx.windows.values():
        if not ctx.editable(win):
            continue

        if not win.focused:
            # TODO: check more here
            assert win.x == 400, 'Side window has a wrong size'


bigSpacing = Cfg()

spacing = 20

bigSpacing.extensions = {Tiler: {'mainSize': 2 / 3, 'border': 5, 'spacing': spacing}}

# TODO: check big spacing


@test('spacing works?', [startX, startWm(bigSpacing), openWins], suit)
async def _bigSpacing(tctx: 'TCtx'):
    ctx: 'Ctx' = tctx.pres[1].data

    await randFocus(ctx)
    assert ctx.focused, 'No focused window'
    checkWin(ctx.focused, 20, 20, 350, 350)

    for win in ctx.windows.values():
        if not ctx.editable(win) or win.id == ctx.focused.id:
            continue

        checkWin(win, 400, None, 170, None)
