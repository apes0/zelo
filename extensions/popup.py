import trio

from typing import TYPE_CHECKING

from lib.extension import Extension, initExt
from extensions.shortcuts import Shortcuts, arun

if TYPE_CHECKING:
    from lib.backends.generic import GWindow
    from lib.ctx import Ctx

# makes popup windows
# similar to yakuake or guake
# NOTE: you can use winfo to find the window name (or xprop -spy) :)


class Popup(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.n = -1
        self.executable: str  # the command
        self.name: str  # name of the popup window
        self.open: tuple
        self.width: int = ctx.screen.width
        self.height: int = ctx.screen.height // 2
        self.x: int = 0
        self.y: int = 0
        self.win: GWindow | None = None
        self.oldFocus: GWindow | None = None

        super().__init__(
            ctx, cfg, resolve={'width': int, 'height': int, 'x': int, 'y': int}
        )

    async def spawn(self):
        e = trio.Event()

        async def createFilter(win: 'GWindow'):
            # a filter to always set the ignore flag of a window to ``True``
            async def ignoreFilter():
                if not win.ignore:
                    win.ignore = True
                return False  # always block the triggering of ignored

            found = False
            for name in await win.names():
                if name == self.name:
                    found = True  # we found a *possible* match
                    break

            if not found:
                return True  # let the event pass, since we didnt find anything

            win.ignored.addFilter(ignoreFilter)
            win.ignore = True

            async def nope(*_a):
                return False

            async def mapFilter():
                # we should have the window now :)
                # TODO: what do we do about windows with startup windows
                self.win = win
                await self.configure()
                await win.unmap()

                # the window has no rights :p
                async def conf():
                    await self.configure()
                    return False  # we supress this event since the only thing we can get from it is someone configuring our window, and we dont want that

                win.mapNotify.addFilter(nope)
                win.mapRequest.addFilter(nope)
                win.configureNotify.addFilter(conf)
                win.configureRequest.addFilter(nope)

                e.set()

                win.mapRequest.removeFilter(m)
                self.ctx.createNotify.removeFilter(n)

                return True  # we handled the mapRequest, but some extensions can use it for something, so we should maybe still send out the event

            m = win.mapRequest.addFilter(mapFilter)

            return True  # we can still send the create notify, since we are marked as ignored

        n = self.ctx.createNotify.addFilter(createFilter)

        self.proc = await trio.lowlevel.open_process(self.executable.split(' '))
        await e.wait()

    async def __ainit__(self):
        await self.spawn()

        shortcuts = await initExt(
            Shortcuts,  # type:ignore
            self.ctx,
            {
                'shortcuts': {
                    self.open: arun(self.ctx, self.toggle),
                }
            },
        )

        if shortcuts:
            shortcuts.register()

        self.addListener(self.ctx.mapNotify, self.toTop)

    async def configure(self):
        if not self.win:
            return

        await self.win.configure(
            newX=self.x,
            newY=self.y + 2 * self.win.borderWidth,
            newWidth=self.width - 2 * self.win.borderWidth,
            newHeight=self.height - 2 * self.win.borderWidth,
        )

    async def toTop(self, _win):
        if not self.win:
            return

        await self.win.toTop()

    async def close(self):
        if not self.win:
            return

        await self.win.unmap()
        await self.win.setFocus(False)
        self.ctx.focusChange.removeListener(self.n)
        if self.oldFocus:
            await self.oldFocus.setFocus(True)

    async def focusChange(self, old, _new):
        assert self.win, 'self.win of popup is not set in focusChange'
        if old and old.id == self.win.id:
            await self.close()

    async def toggle(self, _ctx):
        if not self.win or self.win.destroyed:
            self.win = None
            self.proc.kill()
            await self.spawn()
            await self.toggle(None)
            return

        if self.win.mapped:
            await self.close()
        else:
            self.oldFocus = self.ctx.focused
            await self.configure()
            await self.win.map()
            await self.win.toTop()
            await self.win.setFocus(True)
            self.n = self.ctx.focusChange.addListener(self.focusChange)
