from lib.extension import Extension
from lib.ffi import ffi, lib as xcb
from lib.types import enterNotifyTC, buttonPressTC, charpC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.ctx import Ctx

# i found what enter notify and leave notify do here: (on line 853)
# https://gitlab.gnome.org/GNOME/mutter/-/blob/main/src/x11/events.c

class MouseFocus(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        super().__init__(ctx, cfg)
        self.addListener(xcb.XCB_ENTER_NOTIFY, self.enterNotify)
        self.addListener(xcb.XCB_LEAVE_NOTIFY, self.leaveNotify)
        self.addListener(xcb.XCB_BUTTON_PRESS, self.buttonPress)
        self.addListener(xcb.XCB_MAP_REQUEST, self.mapWindow)

    def mapWindow(self, _event):
        for windowId in self.ctx.windows.keys():
            xcb.xcb_grab_button(
                self.ctx.connection,
                0,
                windowId,
                xcb.XCB_EVENT_MASK_BUTTON_PRESS,
                xcb.XCB_GRAB_MODE_ASYNC,
                xcb.XCB_GRAB_MODE_ASYNC,
                xcb.XCB_NONE,
                0,
                xcb.XCB_BUTTON_INDEX_ANY,
                xcb.XCB_MOD_MASK_ANY,
            )
        xcb.xcb_flush(self.ctx.connection)

    def buttonPress(self, event):
        event = buttonPressTC(event)
        windowId = event.event
        xcb.xcb_ungrab_button(
                self.ctx.connection,
                xcb.XCB_BUTTON_INDEX_ANY,
                windowId,
                xcb.XCB_MOD_MASK_ANY,
            )
        self.ctx.getWindow(windowId).setFocus(True)

    def enterNotify(self, event):
        event = enterNotifyTC(event)
        windowId = event.event
        if windowId == self.ctx.focused.id:
            return
        xcb.xcb_grab_button(
                self.ctx.connection,
                0,
                windowId,
                xcb.XCB_EVENT_MASK_BUTTON_PRESS,
                xcb.XCB_GRAB_MODE_ASYNC,
                xcb.XCB_GRAB_MODE_ASYNC,
                xcb.XCB_NONE,
                0,
                xcb.XCB_BUTTON_INDEX_ANY,
                xcb.XCB_MOD_MASK_ANY,
            )
        xcb.xcb_flush(self.ctx.connection)
    
    def leaveNotify(self, event):
        event = enterNotifyTC(event)
        xcb.xcb_ungrab_button(
                self.ctx.connection,
                xcb.XCB_EVENT_MASK_BUTTON_PRESS,
                event.event,
                xcb.XCB_MOD_MASK_ANY,
            )
        xcb.xcb_flush(self.ctx.connection)
