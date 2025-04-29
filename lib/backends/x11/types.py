from typing import Any

from xcb_cffi import ffi

from ..base import Base


def maxUVal(t: str):
    return (1 << (ffi.sizeof(t) * 8)) - 1


def maxVal(t: str):
    return (1 << (ffi.sizeof(t) * 8 - 1)) - 1


class FFIType:
    def __init__(self, _type) -> None:
        self.type = _type

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return ffi.new(self.type, *args, **kwargs)


intp = FFIType('int*')
intarr = FFIType('int[]')
uintarr = FFIType('unsigned int[]')
charp = FFIType('char*')
charpp = FFIType('char**')
uchararr = FFIType('unsigned char[]')
chararr = FFIType('char[]')
rectangle = FFIType('xcb_rectangle_t*')
keyEvent = FFIType('xcb_key_press_event_t*')  # key release is the same
xcbErrorContext = FFIType('xcb_errors_context_t**')


class Caster:
    def __init__(self, _type) -> None:
        self.type = _type

    def __call__(self, other) -> Any:
        if isinstance(other, Base):
            other = other.obj

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
enterNotifyTC = Caster('xcb_enter_notify_event_t*')  # leave notify is the same
destroyNotifyTC = Caster('xcb_destroy_notify_event_t*')
motionNotifyTC = Caster('xcb_motion_notify_event_t*')
mapNotifyTC = Caster('xcb_map_notify_event_t *')
unmapNotifyTC = Caster('xcb_unmap_notify_event_t *')
ExposeTC = Caster('xcb_expose_event_t *')
ReparentNotifyTC = Caster('xcb_reparent_notify_event_t *')
PropertyNotifyTC = Caster('xcb_property_notify_event_t *')
# requests
atomNameRequestTC = Caster('xcb_get_atom_name_request_t *')
genericErrorTC = Caster('xcb_generic_error_t*')
# others
voidpC = Caster('void*')
charpC = Caster('char*')
intpC = Caster('int*')
keysymC = Caster('xcb_keysym_t*')
# xrandr
randrNotifyTC = Caster('xcb_randr_notify_event_t *')
# icccm
icccmWmHintsTC = Caster('xcb_icccm_wm_hints_t *')
