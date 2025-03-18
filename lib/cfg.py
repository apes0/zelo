from typing import TYPE_CHECKING, Callable

from extensions.animation import Animation
from extensions.borders import Borders
from extensions.fakeMonitors import FakeDisplays
from extensions.mouse import Mouse
from extensions.mouseFocus import MouseFocus
from extensions.shortcuts import Shortcuts
from extensions.tiler import Tiler
from extensions.wallpaper import Wallpaper
from extensions.widget import Widget
from extensions.widgets.bar import Bar
from extensions.widgets.clock import Clock
from extensions.widgets.nowPlaying import NowPlaying
from extensions.widgets.text import Text
from extensions.workspaces import Workspaces
from extensions.winfo import Winfo
from extensions.share import ShareServer, ShareClient
from extensions.tabs import Tabs

from lib._cfg import Cfg
from lib.api.keys import Key, Mod
from lib.debcfg import cfg as debcfg

from utils.fns import spawn, stop, toCursor
from utils.layout import Layout
from utils.ratio import Ratio
from utils.theme import Theme
from utils.log import logTerm, log

# debcfg['all'] = True

logTerm()
# ('log')

if TYPE_CHECKING:
    from lib.backends.generic import GKey, GMod

cfg = Cfg()

keys: dict[tuple[tuple['GKey', ...], 'GMod'], Callable] = {
    #    ((Key('super_l'),), Mod('')): lambda _ctx: spawn('ulauncher-toggle'),
    ((Key('t'),), Mod('control')): lambda ctx: spawn('alacritty'),
    ((Key('s'),), Mod('control')): lambda ctx: ctx.nurs.start_soon(stop, ctx),
    ((Key('g'),), Mod('control')): lambda _ctx: spawn('glxgears'),
    ((Key('x'),), Mod('control')): lambda ctx: (
        ctx.startSoon(ctx.focused.screenshot) if ctx.focused else None
    ),
    # ((Key('m'),), Mod('control')): lambda ctx: (
    #     toCursor(ctx, ctx.focused) if ctx.focused else None
    # ),
}

wall = 'wall.png'

theme = Theme(0x9999D6, 0x393966, [])
cfg.theme = theme

# layouts

main = Layout()
bar, main = main.hsplit(0.175, 0.025)
main.unspace()

# extensions and their config

cfg.extensions = {
    #    FakeDisplays: {'displays': [[480, 480]]},
    Tiler: {
        'mainSize': 2 / 3,
        'border': 5,
        'spacing': 10,
        #        'topSpacing': main.y,
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
        'widgets': [
            (
                Bar,
                {
                    'x': bar.x,
                    'y': bar.y,
                    'width': bar.width,
                    'height': bar.height,
                    'widgets': [
                        (
                            Clock,
                            {
                                'font': 'Ubuntu 33',
                                'fmt': '%X',
                            },
                        ),
                        (
                            NowPlaying,
                            {
                                'font': 'Ubuntu 33',
                                'width': 400,
                            },
                        ),
                        (Text, {'text': 'Hello World!', 'font': 'Ubuntu 33'}),
                    ],
                },
            )
        ]
    },
    Mouse: {},
    Tabs: {},
    Borders: {'width': 5, 'focused': theme.fore, 'unfocused': theme.back},
    #    Winfo: {},
    #    ShareServer:{},
    #    ShareClient:{'addr': '0.0.0.0'},
    #    Animation: {},
}

# startup

# spawn('ulauncher')
