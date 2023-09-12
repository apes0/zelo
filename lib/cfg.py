from lib.utils import spawn, stop
from lib.backends.ffi import load

from extensions.tiler import Tiler
from extensions.workspaces import Workspaces
from extensions.mouseFocus import MouseFocus
from extensions.wallpaper import Wallpaper
from extensions.shotcuts import Shortcuts

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from lib.backends.generic import GKey, GMod

key = load('keys')
Key: type = key.Key
Mod: type = key.Mod

keys: dict[tuple[tuple['GKey', ...], 'GMod'], Callable] = {
    ((Key('super_l'),), Mod('')): lambda _ctx: spawn('ulauncher-toggle'),
    ((Key('t'),), Mod('control')): lambda ctx: spawn('alacritty'),
    ((Key('s'),), Mod('control')): lambda ctx: stop(ctx),
    ((Key('g'),), Mod('control')): lambda _ctx: spawn('glxgears'),
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
        'prev': ((Key('left'),), Mod('control')),
        'next': ((Key('right'),), Mod('control')),
    },
}

# startup

spawn('ulauncher')
