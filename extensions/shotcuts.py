from lib.extension import Extension
from lib.ffi import ffi, lib as xcb
from lib.types import keyPressTC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.ctx import Ctx


class Shortcuts(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        super().__init__(ctx, cfg)
        self.keys = []
        self.shortcuts: dict

        self.addListener(xcb.XCB_KEY_PRESS, self.keyPress)
        self.addListener(xcb.XCB_KEY_RELEASE, self.keyRelease)

        self.register()

    def register(self):
        keys = self.shortcuts.keys()
        # NOTE: use xcb.XCB_GRAB_ANY for key to find the keycode
        # keys = [xcb.XCB_GRAB_ANY]
        self.ignore = [
            xcb.XCB_MOD_MASK_LOCK,
            xcb.XCB_MOD_MASK_2,
            0,
        ]  # TODO: get all combinations (im too lazy to do this rn)
        for _mod in [*self.ignore, sum(self.ignore)]:
            for key in keys:
                mod = key[1]
                for key in key[0]:
                    xcb.xcb_grab_key(
                        self.ctx.connection,
                        0,
                        self.ctx._root,
                        mod | _mod,
                        key,
                        xcb.XCB_GRAB_MODE_ASYNC,
                        xcb.XCB_GRAB_MODE_ASYNC,
                    )

    def keyPress(self, event):
        event = keyPressTC(event)
        key = event.detail
        for idx, _key in enumerate(self.keys):
            if key == _key:
                break
            if key < _key:
                self.keys.insert(idx, key)
                break
        else:
            self.keys.append(key)
        fn = self.shortcuts.get((tuple(self.keys), event.state & ~sum(self.ignore)))
        if fn:
            fn(self.ctx)
            self.keys = []

    def keyRelease(self, event):
        event = keyPressTC(event)
        key = event.detail
        if key in self.keys:
            self.keys.remove(key)
        else:
            # NOTE: if the key doesn't exist in the list of pressed keys, then it is a modifier, and
            # thus, the keys list should be cleared
            self.keys.clear()
