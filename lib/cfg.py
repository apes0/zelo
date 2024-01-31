from lib.utils import Ratio, Theme, spawn, stop
from lib.api.keys import Key, Mod
from lib._cfg import Cfg

from extensions.tiler import Tiler
from extensions.workspaces import Workspaces
from extensions.mouseFocus import MouseFocus
from extensions.wallpaper import Wallpaper
from extensions.shortcuts import Shortcuts
from extensions.fakeMonitors import FakeDisplays
from extensions.widget import Widget
from extensions.widgets.clock import Clock
from extensions.widgets.nowPlaying import NowPlaying
from extensions.widgets.hbar import Bar
from extensions.animation import Animation

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from lib.backends.generic import GKey, GMod

cfg = Cfg()

keys: dict[tuple[tuple['GKey', ...], 'GMod'], Callable] = {
    #    ((Key('super_l'),), Mod('')): lambda _ctx: spawn('ulauncher-toggle'),
    ((Key('t'),), Mod('control')): lambda ctx: spawn('alacritty'),
    ((Key('s'),), Mod('control')): lambda ctx: stop(ctx),
    ((Key('g'),), Mod('control')): lambda _ctx: spawn('glxgears'),
    ((Key('x'),), Mod('control')): lambda ctx: ctx.nurs.start_soon(ctx.focused.close)
    if ctx.focused
    else None,
}

# ? maybe export this to a plugin
cfg.focusedColor = 0x9999D6
cfg.unfocusedColor = 0x393966
# unfocusedColor = 0x1CEEEE
# focusedColor = 0xC0FFEE

theme = Theme(cfg.focusedColor, cfg.unfocusedColor)

# extensions and their config

cfg.extensions = {
    FakeDisplays: {'displays': [[480, 480]]},  # just here for testing with xephyr
    Tiler: {'mainSize': 2 / 3, 'border': Ratio(0.015), 'spacing': Ratio(0.02)},
    MouseFocus: {},
    Wallpaper: {'wall': 'wall.png'},
    #    Wallpaper: {'wall': 'video.gif', 'video': True},
    Shortcuts: {'shortcuts': keys},
    Workspaces: {
        'prev': ((Key('left'), Key('super_l')), Mod('control')),
        'next': ((Key('right'), Key('super_l')), Mod('control')),
        'move': (
            (Key('m'), Key('super_l')),
            Mod('control'),
        ),
    },
    #    Widget: {
    #        'widgets': {
    #            Bar: {
    #                'x': Ratio(0.05, width=True),
    #                'y': Ratio(0.02, height=True),
    #                'width': Ratio(0.9, width=True),
    #                'height': Ratio(0.1, height=True),
    #                'back': theme,
    #                'widgets': {
    #                    Clock: {
    #                        'font': 'Ubuntu 23',
    #                        'fmt': '%X',
    #                        'fore': theme,
    #                        'back': theme,
    #                    },
    #                    # NowPlaying: {
    #                    #     'font': 'Ubuntu 23',
    #                    #     'fore': theme,
    #                    #     'back': theme,
    #                    # },
    #                },
    #            }
    #        }
    #    },
    #    Animation: {},
}

# startup

# spawn('ulauncher')
