from lib.utils import spawn, stop
from lib.api.keys import Key, Mod
from lib._cfg import Cfg

from extensions.tiler import Tiler
from extensions.workspaces import Workspaces
from extensions.mouseFocus import MouseFocus
from extensions.wallpaper import Wallpaper
from extensions.shortcuts import Shortcuts
from extensions.fakeMonitors import FakeDisplays
from extensions.bar import Bar

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from lib.backends.generic import GKey, GMod

cfg = Cfg()

keys: dict[tuple[tuple['GKey', ...], 'GMod'], Callable] = {
    #    ((Key('super_l'),), Mod('')): lambda _ctx: spawn('ulauncher-toggle'),
    ((Key('t'),), Mod('control')): lambda ctx: spawn('alacritty'),
    ((Key('s'),), Mod('control')): lambda ctx: stop(ctx),
    ((Key('g'),), Mod('control')): lambda _ctx: spawn('glxgears'),
    ((Key('x'),), Mod('control')): lambda ctx: ctx.focused.close()
    if ctx.focused
    else None,
}

cfg.focusedColor = 0x9999D6
cfg.unfocusedColor = 0x393966
# unfocusedColor = 0x1CEEEE
# focusedColor = 0xC0FFEE

# extensions and their config

cfg.extensions = {
    FakeDisplays: {'displays': [[480, 480]]},  # just here for testing with xephyr
    Tiler: {'mainSize': 2 / 3, 'border': 5, 'spacing': 10},
    MouseFocus: {},
    #    Wallpaper: {'wall': 'wall.png'},
    Wallpaper: {'wall': 'video.gif', 'video': True},
    Shortcuts: {'shortcuts': keys},
    Workspaces: {
        'prev': ((Key('left'), Key('super_l')), Mod('control')),
        'next': ((Key('right'), Key('super_l')), Mod('control')),
        'move': (
            (Key('m'), Key('super_l')),
            Mod('control'),
        ),  # TODO: this doesnt work :/
        #    Bar: {'width': 100, 'height': 100, 'x': 10, 'y': 10},
    },
}

# startup

# spawn('ulauncher')
