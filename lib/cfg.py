from lib.utils import spawn, stop
from lib.api.keys import Key, Mod

from extensions.tiler import Tiler
from extensions.workspaces import Workspaces
from extensions.mouseFocus import MouseFocus
from extensions.wallpaper import Wallpaper
from extensions.shotcuts import Shortcuts
from extensions.fakeMonitors import FakeDisplays

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from lib.backends.generic import GKey, GMod


keys: dict[tuple[tuple['GKey', ...], 'GMod'], Callable] = {
    ((Key('super_l'),), Mod('')): lambda _ctx: spawn('ulauncher-toggle'),
    ((Key('t'),), Mod('control')): lambda ctx: spawn('alacritty'),
    ((Key('s'),), Mod('control')): lambda ctx: stop(ctx),
    ((Key('g'),), Mod('control')): lambda _ctx: spawn('glxgears'),
    ((Key('x'),), Mod('mod1')): lambda ctx: ctx.focused.close()
    if ctx.focused
    else None,
}

focusedColor = 0x9999D6
unfocusedColor = 0x393966
# unfocusedColor = 0x1CEEEE
# focusedColor = 0xC0FFEE

# extensions and their config

extensions = {
    FakeDisplays: {'displays': [[960, 960]]},  # just here for testing with xephyr
    Tiler: {'mainSize': 2 / 3, 'border': 5, 'spacing': 10},
    MouseFocus: {},
    Wallpaper: {'wall': 'wall.png'},
    Shortcuts: {'shortcuts': keys},
    Workspaces: {
        'prev': ((Key('left'), Key('super_l')), Mod('control')),
        'next': ((Key('right'), Key('super_l')), Mod('control')),
    },
}

# startup

spawn('ulauncher')
