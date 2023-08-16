from extensions.workspaces import Workspaces
from lib.utils import spawn, stop
from lib.ffi import lib as xcb
from extensions.tiler import Tiler
from extensions.mouseFocus import MouseFocus
from extensions.wallpaper import Wallpaper
from extensions.shotcuts import Shortcuts

# todo: move to xkb (idk how tho)

#! set the keys in the tuple in increasing order, else your shortcuts will **NOT** work!!!!
keys = {
    ((133,), 0): lambda _ctx: spawn('ulauncher-toggle'),
    ((28,), xcb.XCB_MOD_MASK_CONTROL): lambda ctx: spawn('alacritty'),
    ((39,), xcb.XCB_MOD_MASK_CONTROL): lambda ctx: stop(ctx),
    ((42,), xcb.XCB_MOD_MASK_CONTROL): lambda _ctx: spawn('glxgears'),
}

focusedColor = 0x9999D6
unfocusedColor = 0x393966

# extensions and their config

extensions = {
    Tiler: {'mainSize': 2 / 3, 'border': 5, 'spacing': 10},
    MouseFocus: {},
    Wallpaper: {'wall': 'wall.png'},
    Shortcuts: {'shortcuts': keys},
    Workspaces: {
        'prev': ((113,), xcb.XCB_MOD_MASK_CONTROL),
        'next': ((114,), xcb.XCB_MOD_MASK_CONTROL),
    },
}

# startup

spawn('ulauncher')
