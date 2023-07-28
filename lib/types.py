from typing import Any
from .ffi import ffi


class FFIType:
    def __init__(self, _type) -> None:
        self.type = _type

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return ffi.new(self.type, *args, **kwargs)


intp = FFIType('int*')
intarr = FFIType('int[]')
uintarr = FFIType('unsigned int[]')
charp = FFIType('char*')
chararr = FFIType('char[]')


class Caster:
    def __init__(self, _type) -> None:
        self.type = _type

    def __call__(self, other) -> Any:
        return ffi.cast(self.type, other)


# event types

buttonPressTC = Caster('xcb_button_press_event_t*')  # button release is the same
keyPressTC = Caster('xcb_key_press_event_t*')  # key release is the same
focusInTC = Caster('xcb_focus_in_event_t*')  # focus out is the same
clientMessageTC = Caster('xcb_client_message_event_t*')
mapRequestTC = Caster('xcb_map_request_event_t*')
confRequestTC = Caster('xcb_configure_request_event_t*')
createNotifyTC = Caster('xcb_create_notify_event_t*')
confNotifyTC = Caster('xcb_configure_notify_event_t*')
enterNotifyTC = Caster('xcb_enter_notify_event_t*')
destroyNotifyTC = Caster('xcb_destroy_notify_event_t*')
# motionNotifyTC = Caster('xcb_motion_notify_event_t*')
mapNotifyTC = Caster('xcb_map_notify_event_t *')
unmapNotifyTC = Caster('xcb_unmap_notify_event_t *')
# requests
atomNameRequestTC = Caster('xcb_get_atom_name_request_t *')
