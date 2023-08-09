from lib.utils import spawn, stop
from lib.ffi import lib as xcb
from typing import TYPE_CHECKING
from extensions.tiler import Tiler
from extensions.mouseFocus import MouseFocus
from extensions.wallpaper import Wallpaper

if TYPE_CHECKING:
    from lib.ctx import Ctx
    from lib.window import Window


# todo: move to xkb (idk how tho)

#! set the keys in the tuple in increasing order, else your shortcuts will **NOT** work!!!!
keys = {
    ((133,), 0): lambda _ctx: spawn('ulauncher-toggle'),
    ((28,), xcb.XCB_MOD_MASK_CONTROL): lambda ctx: spawn('xterm -bg black -fg white'),
    ((39,), xcb.XCB_MOD_MASK_CONTROL): lambda ctx: stop(ctx),
    ((42,), xcb.XCB_MOD_MASK_CONTROL): lambda _ctx: spawn('glxgears'),
}

focusedColor = 0x696996
unfocusedColor = 0x393966
# unfocusedColor = 0x494976

# managers

extensions = {
    Tiler: {'mainSize': 2/3, 'border': 5, 'spacing': 15},
    MouseFocus : {},
    Wallpaper: {'wall': 'wall.png'}
}

# startup
