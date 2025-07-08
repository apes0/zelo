from typing import TYPE_CHECKING
from collections.abc import Callable

from extensions.borders import Borders
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
from extensions.popup import Popup
from lib._cfg import Cfg
from lib.api.keys import Key, Mod
from utils.fns import spawn, stop
from utils.layout import Layout
from utils.log import logTerm
from utils.theme import Theme

# debcfg['all'] = True

logTerm()
# log('/tmp/log')

if TYPE_CHECKING:
    from lib.backends.generic import GKey, GMod

cfg = Cfg()

keys: dict[tuple[tuple['GKey', ...], 'GMod'], Callable] = {
    # ((Key('any'),), Mod('any')): lambda ctx: None,
    #    ((Key('super_l'),), Mod('')): lambda _ctx: spawn('ulauncher-toggle'),
    ((Key('t'),), Mod('control')): lambda ctx: spawn(
        'xterm -font lucidasanstypewriter-24 -bg black -fg white'
    ),
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
bar, main = main.hsplit(0.08, 0, 0.025)

# extensions and their config

cfg.extensions = {
    #    FakeDisplays: {'displays': [[480, 480]]},
    Tiler: {
        'mainSize': 2 / 3,
        'border': 5,
        'spacing': 10,
        'topSpacing': main.y,
    },
    MouseFocus: {},
    Wallpaper: {'wall': wall},
    # Wallpaper: {'wall': 'video.gif', 'video': True},
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
                        # (Button, {'back': 0, 'fn': lambda *a: print(a)}),
                    ],
                },
            )
        ]
    },
    Mouse: {'cursor': 'pirate'},
    # Tabs: {},
    Borders: {'width': 5, 'focused': theme.fore, 'unfocused': theme.back},
    Popup: {
        'width': main.width,
        'x': main.x,
        'executable': 'xterm -font lucidasanstypewriter-24 -bg black -fg white',
        'name': 'xterm',
        # 'executable': 'xournalpp',
        # 'name': 'com.github.xournalpp.xournalpp',
        'open': ((Key('f12'),), Mod('control')),
        'y': main.unspace().y,
    },
    # Blank: {'timeout': 10},
    # Winfo: {},
    #    ShareServer:{},
    #    ShareClient:{'addr': '0.0.0.0'},
    # Animation: {},
}

# startup

# spawn('ulauncher')
