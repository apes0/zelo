from lib.utils import spawn, stop
from lib.ffi import lib as xcb
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.ctx import Ctx
    from lib.window import Window


# todo: move to xkb

#! set the keys in the tuple in increasing order, else your shortcuts will **NOT** work!!!!
keys = {
    ((133,), 0): lambda _ctx: spawn('ulauncher-toggle'),
    ((42, 43, 44), xcb.XCB_MOD_MASK_CONTROL): lambda _ctx: spawn('gedit'),
    ((39,), xcb.XCB_MOD_MASK_CONTROL): lambda ctx: stop(ctx),
    ((56,), xcb.XCB_MOD_MASK_CONTROL): lambda _ctx: spawn('glxgears'),
}
focusedColor = 0x696996
unfocusedColor = 0x393966
# unfocusedColor = 0x494976

# managers


def createWindow(window: 'Window', ctx: 'Ctx'):
    window.configure(
        newX=len(ctx.windows) * 30,
        newY=len(ctx.windows) * 10,
        newBorderWidth=5,
    )


# startup

spawn('ulauncher')
