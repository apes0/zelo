import logging
from utils.layout import Layout
from utils.ratio import Ratio
from utils.theme import Theme
from utils.fns import spawn, stop
from lib.api.keys import Key, Mod
from lib._cfg import Cfg

from extensions.vstack import Tiler
from extensions.workspaces import Workspaces
from extensions.mouseFocus import MouseFocus
from extensions.wallpaper import Wallpaper
from extensions.shortcuts import Shortcuts
from extensions.widget import Widget
from extensions.widgets.clock import Clock
from extensions.widgets.nowPlaying import NowPlaying
from extensions.widgets.hbar import Bar
from extensions.mouse import Mouse

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from lib.backends.generic import GKey, GMod

logging.basicConfig(level=logging.DEBUG)

cfg = Cfg()

keys: dict[tuple[tuple['GKey', ...], 'GMod'], Callable] = {
    #    ((Key('super_l'),), Mod('')): lambda _ctx: spawn('ulauncher-toggle'),
    ((Key('t'),), Mod('control')): lambda ctx: spawn('alacritty'),
    ((Key('s'),), Mod('control')): lambda ctx: stop(ctx),
    ((Key('g'),), Mod('control')): lambda _ctx: spawn('glxgears'),
    ((Key('x'),), Mod('control')): lambda ctx: (
        ctx.nurs.start_soon(ctx.focused.close) if ctx.focused else None
    ),
}

wall = 'wall.png'

theme = Theme(0x9999D6, 0x393966, [])
cfg.theme = theme

cfg.focusedColor = theme.fore
cfg.unfocusedColor = theme.back

# ? maybe export this to a plugin
cfg.focusedColor = theme.fore
cfg.unfocusedColor = theme.back

# layouts

main = Layout()
bar, main = main.hsplit(0.175, 0.025)
main.unspace()

# extensions and their config

cfg.extensions = {
    Tiler: {
        'mainSize': 2 / 3,
        'border': 5,
        'spacing': 10,
        'topSpacing': main.y,
    },
    MouseFocus: {},
    Wallpaper: {'wall': wall},
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
    Widget: {
        'widgets': {
            Bar: {
                'x': bar.x,
                'y': bar.y,
                'width': bar.width,
                'height': bar.height,
                'widgets': {
                    Clock: {
                        'font': 'Ubuntu 23',
                        'fmt': '%X',
                    },
                    NowPlaying: {
                        'font': 'Ubuntu 23',
                    },
                },
            }
        }
    },
    Mouse: {},
    #    Animation: {},
}

# startup

# spawn('ulauncher')
