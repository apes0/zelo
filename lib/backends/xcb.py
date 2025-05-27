from _cffi_backend import _CDataBase
from xcb_cffi import lib, ffi
from typing import Any, Literal
from .base import Base, parseArgs, Ptr, CPtr, void

NULL = ffi.NULL

# types
# skipping Xcbkeysymbols, because its not fully defined
class Xcbkeysymbols(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
# skipping ExtensionInfoT, because its not fully defined
class ExtensionInfoT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
XcbAtomT = int
class XcbButtonPressEventT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.child: XcbWindowT = obj.child
        self.detail: XcbButtonT = obj.detail
        self.event: XcbWindowT = obj.event
        self.eventX: int = obj.event_x
        self.eventY: int = obj.event_y
        self.pad0: int = obj.pad0
        self.responseType: int = obj.response_type
        self.root: XcbWindowT = obj.root
        self.rootX: int = obj.root_x
        self.rootY: int = obj.root_y
        self.sameScreen: int = obj.same_screen
        self.sequence: int = obj.sequence
        self.state: int = obj.state
        self.time: XcbTimestampT = obj.time
XcbButtonT = int
class XcbClientMessageDataT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.data16: int = obj.data16
        self.data32: int = obj.data32
        self.data8: int = obj.data8
class XcbClientMessageEventT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.data: XcbClientMessageDataT = obj.data
        self.format: int = obj.format
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
        self.type: int = obj.type
        self.window: XcbWindowT = obj.window
XcbColormapT = int
class XcbConfigureNotifyEventT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.aboveSibling: XcbWindowT = obj.above_sibling
        self.borderWidth: int = obj.border_width
        self.event: XcbWindowT = obj.event
        self.height: int = obj.height
        self.overrideRedirect: int = obj.override_redirect
        self.pad0: int = obj.pad0
        self.pad1: int = obj.pad1
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
        self.width: int = obj.width
        self.window: XcbWindowT = obj.window
        self.x: XcbWindowT = obj.x
        self.y: int = obj.y
class XcbConfigureRequestEventT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.borderWidth: int = obj.border_width
        self.height: int = obj.height
        self.parent: XcbWindowT = obj.parent
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
        self.sibling: XcbWindowT = obj.sibling
        self.stackMode: int = obj.stack_mode
        self.valueMask: int = obj.value_mask
        self.width: int = obj.width
        self.window: XcbWindowT = obj.window
        self.x: XcbWindowT = obj.x
        self.y: int = obj.y
# skipping XcbConnectionT, because its not fully defined
class XcbConnectionT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
class XcbCreateNotifyEventT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.borderWidth: int = obj.border_width
        self.height: int = obj.height
        self.overrideRedirect: int = obj.override_redirect
        self.pad0: int = obj.pad0
        self.pad1: int = obj.pad1
        self.parent: XcbWindowT = obj.parent
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
        self.width: int = obj.width
        self.window: XcbWindowT = obj.window
        self.x: XcbWindowT = obj.x
        self.y: int = obj.y
XcbCursorT = int
class XcbDestroyNotifyEventT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.event: XcbWindowT = obj.event
        self.pad0: int = obj.pad0
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
        self.window: XcbWindowT = obj.window
class XcbDpmsCapableCookieT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.sequence: int = obj.sequence
class XcbDpmsCapableReplyT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.capable: int = obj.capable
        self.length: int = obj.length
        self.pad0: int = obj.pad0
        self.pad1: int = obj.pad1
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
class XcbDpmsGetTimeoutsCookieT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.sequence: int = obj.sequence
class XcbDpmsGetTimeoutsReplyT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.length: int = obj.length
        self.offTimeout: int = obj.off_timeout
        self.pad0: int = obj.pad0
        self.pad1: int = obj.pad1
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
        self.standbyTimeout: int = obj.standby_timeout
        self.suspendTimeout: int = obj.suspend_timeout
class XcbDpmsInfoCookieT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.sequence: int = obj.sequence
class XcbDpmsInfoReplyT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.length: int = obj.length
        self.pad0: int = obj.pad0
        self.pad1: int = obj.pad1
        self.powerLevel: int = obj.power_level
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
        self.state: int = obj.state
XcbDrawableT = int
class XcbEnterNotifyEventT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.child: XcbWindowT = obj.child
        self.detail: int = obj.detail
        self.event: XcbWindowT = obj.event
        self.eventX: int = obj.event_x
        self.eventY: int = obj.event_y
        self.mode: int = obj.mode
        self.responseType: int = obj.response_type
        self.root: XcbWindowT = obj.root
        self.rootX: int = obj.root_x
        self.rootY: int = obj.root_y
        self.sameScreenFocus: int = obj.same_screen_focus
        self.sequence: int = obj.sequence
        self.state: int = obj.state
        self.time: XcbTimestampT = obj.time
# skipping XcbErrorsContextT, because its not fully defined
class XcbErrorsContextT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
class XcbExposeEventT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.count: int = obj.count
        self.height: int = obj.height
        self.pad0: int = obj.pad0
        self.pad1: int = obj.pad1
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
        self.width: int = obj.width
        self.window: XcbWindowT = obj.window
        self.x: XcbWindowT = obj.x
        self.y: int = obj.y
# skipping XcbExtensionT, because its not fully defined
class XcbExtensionT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
class XcbFocusInEventT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.detail: int = obj.detail
        self.event: XcbWindowT = obj.event
        self.mode: int = obj.mode
        self.pad0: int = obj.pad0
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
XcbFontT = int
XcbGcontextT = int
class XcbGenericErrorT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.errorCode: int = obj.error_code
        self.fullSequence: int = obj.full_sequence
        self.majorCode: int = obj.major_code
        self.minorCode: int = obj.minor_code
        self.pad: int = obj.pad
        self.pad0: int = obj.pad0
        self.resourceId: int = obj.resource_id
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
class XcbGenericEventT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.fullSequence: int = obj.full_sequence
        self.pad: int = obj.pad
        self.pad0: int = obj.pad0
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
class XcbGetAtomNameCookieT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.sequence: int = obj.sequence
class XcbGetAtomNameReplyT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.length: int = obj.length
        self.nameLen: int = obj.name_len
        self.pad0: int = obj.pad0
        self.pad1: int = obj.pad1
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
class XcbGetAtomNameRequestT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.atom: XcbAtomT = obj.atom
        self.length: int = obj.length
        self.majorOpcode: int = obj.major_opcode
        self.pad0: int = obj.pad0
class XcbGetGeometryCookieT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.sequence: int = obj.sequence
class XcbGetGeometryReplyT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.borderWidth: int = obj.border_width
        self.depth: int = obj.depth
        self.height: int = obj.height
        self.length: int = obj.length
        self.pad0: int = obj.pad0
        self.responseType: int = obj.response_type
        self.root: XcbWindowT = obj.root
        self.sequence: int = obj.sequence
        self.width: int = obj.width
        self.x: XcbWindowT = obj.x
        self.y: int = obj.y
class XcbGetImageCookieT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.sequence: int = obj.sequence
class XcbGetImageReplyT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.depth: int = obj.depth
        self.length: int = obj.length
        self.pad0: int = obj.pad0
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
        self.visual: XcbVisualidT = obj.visual
class XcbGetKeyboardMappingCookieT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.sequence: int = obj.sequence
class XcbGetKeyboardMappingReplyT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.keysymsPerKeycode: int = obj.keysyms_per_keycode
        self.length: int = obj.length
        self.pad0: int = obj.pad0
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
class XcbGetModifierMappingCookieT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.sequence: int = obj.sequence
class XcbGetModifierMappingReplyT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.keycodesPerModifier: int = obj.keycodes_per_modifier
        self.length: int = obj.length
        self.pad0: int = obj.pad0
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
class XcbGetPropertyCookieT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.sequence: int = obj.sequence
class XcbGetPropertyReplyT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.bytesAfter: int = obj.bytes_after
        self.format: int = obj.format
        self.length: int = obj.length
        self.pad0: int = obj.pad0
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
        self.type: int = obj.type
        self.valueLen: int = obj.value_len
class XcbGetWindowAttributesCookieT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.sequence: int = obj.sequence
class XcbGetWindowAttributesReplyT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.Class: int = obj._class
        self.allEventMasks: int = obj.all_event_masks
        self.backingPixel: int = obj.backing_pixel
        self.backingPlanes: int = obj.backing_planes
        self.backingStore: int = obj.backing_store
        self.bitGravity: int = obj.bit_gravity
        self.colormap: XcbColormapT = obj.colormap
        self.doNotPropagateMask: int = obj.do_not_propagate_mask
        self.length: int = obj.length
        self.mapIsInstalled: int = obj.map_is_installed
        self.mapState: int = obj.map_state
        self.overrideRedirect: int = obj.override_redirect
        self.pad0: int = obj.pad0
        self.responseType: int = obj.response_type
        self.saveUnder: int = obj.save_under
        self.sequence: int = obj.sequence
        self.visual: XcbVisualidT = obj.visual
        self.winGravity: int = obj.win_gravity
        self.yourEventMask: int = obj.your_event_mask
class XcbIcccmWmHintsT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.flags: int = obj.flags
        self.iconMask: XcbPixmapT = obj.icon_mask
        self.iconPixmap: XcbPixmapT = obj.icon_pixmap
        self.iconWindow: XcbWindowT = obj.icon_window
        self.iconX: int = obj.icon_x
        self.iconY: int = obj.icon_y
        self.initialState: int = obj.initial_state
        self.input: int = obj.input
        self.windowGroup: XcbWindowT = obj.window_group
class XcbImageT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.base: Ptr[void] = obj.base
        self.bitOrder: XcbImageOrderT = obj.bit_order
        self.bpp: int = obj.bpp
        self.byteOrder: XcbImageOrderT = obj.byte_order
        self.data: Ptr[int] = obj.data
        self.depth: int = obj.depth
        self.format: XcbImageFormatT = obj.format
        self.height: int = obj.height
        self.planeMask: int = obj.plane_mask
        self.scanlinePad: int = obj.scanline_pad
        self.size: int = obj.size
        self.stride: int = obj.stride
        self.unit: int = obj.unit
        self.width: int = obj.width
class XcbInternAtomCookieT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.sequence: int = obj.sequence
class XcbInternAtomReplyT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.atom: XcbAtomT = obj.atom
        self.length: int = obj.length
        self.pad0: int = obj.pad0
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
class XcbKeyPressEventT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.child: XcbWindowT = obj.child
        self.detail: XcbKeycodeT = obj.detail
        self.event: XcbWindowT = obj.event
        self.eventX: int = obj.event_x
        self.eventY: int = obj.event_y
        self.pad0: int = obj.pad0
        self.responseType: int = obj.response_type
        self.root: XcbWindowT = obj.root
        self.rootX: int = obj.root_x
        self.rootY: int = obj.root_y
        self.sameScreen: int = obj.same_screen
        self.sequence: int = obj.sequence
        self.state: int = obj.state
        self.time: XcbTimestampT = obj.time
# skipping XcbKeySymbolsT, because its not fully defined
class XcbKeySymbolsT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
XcbKeycodeT = int
XcbKeysymT = int
class XcbMapNotifyEventT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.event: XcbWindowT = obj.event
        self.overrideRedirect: int = obj.override_redirect
        self.pad0: int = obj.pad0
        self.pad1: int = obj.pad1
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
        self.window: XcbWindowT = obj.window
class XcbMapRequestEventT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.pad0: int = obj.pad0
        self.parent: XcbWindowT = obj.parent
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
        self.window: XcbWindowT = obj.window
class XcbMotionNotifyEventT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.child: XcbWindowT = obj.child
        self.detail: int = obj.detail
        self.event: XcbWindowT = obj.event
        self.eventX: int = obj.event_x
        self.eventY: int = obj.event_y
        self.pad0: int = obj.pad0
        self.responseType: int = obj.response_type
        self.root: XcbWindowT = obj.root
        self.rootX: int = obj.root_x
        self.rootY: int = obj.root_y
        self.sameScreen: int = obj.same_screen
        self.sequence: int = obj.sequence
        self.state: int = obj.state
        self.time: XcbTimestampT = obj.time
XcbPixmapT = int
class XcbPropertyNotifyEventT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.atom: XcbAtomT = obj.atom
        self.pad0: int = obj.pad0
        self.pad1: int = obj.pad1
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
        self.state: int = obj.state
        self.time: XcbTimestampT = obj.time
        self.window: XcbWindowT = obj.window
class XcbQueryExtensionCookieT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.sequence: int = obj.sequence
class XcbQueryExtensionReplyT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.firstError: int = obj.first_error
        self.firstEvent: int = obj.first_event
        self.length: int = obj.length
        self.majorOpcode: int = obj.major_opcode
        self.pad0: int = obj.pad0
        self.present: int = obj.present
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
class XcbQueryPointerCookieT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.sequence: int = obj.sequence
class XcbQueryPointerReplyT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.child: XcbWindowT = obj.child
        self.length: int = obj.length
        self.mask: int = obj.mask
        self.pad0: int = obj.pad0
        self.responseType: int = obj.response_type
        self.root: XcbWindowT = obj.root
        self.rootX: int = obj.root_x
        self.rootY: int = obj.root_y
        self.sameScreen: int = obj.same_screen
        self.sequence: int = obj.sequence
        self.winX: int = obj.win_x
        self.winY: int = obj.win_y
class XcbQueryTreeCookieT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.sequence: int = obj.sequence
class XcbQueryTreeReplyT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.childrenLen: int = obj.children_len
        self.length: int = obj.length
        self.pad0: int = obj.pad0
        self.pad1: int = obj.pad1
        self.parent: XcbWindowT = obj.parent
        self.responseType: int = obj.response_type
        self.root: XcbWindowT = obj.root
        self.sequence: int = obj.sequence
class XcbRandrCrtcChangeIteratorT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.data: CPtr[XcbRandrCrtcChangeT] = obj.data
        self.index: int = obj.index
        self.rem: int = obj.rem
class XcbRandrCrtcChangeT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.crtc: XcbRandrCrtcT = obj.crtc
        self.height: int = obj.height
        self.mode: XcbRandrModeT = obj.mode
        self.pad0: int = obj.pad0
        self.rotation: int = obj.rotation
        self.timestamp: XcbTimestampT = obj.timestamp
        self.width: int = obj.width
        self.window: XcbWindowT = obj.window
        self.x: XcbTimestampT = obj.x
        self.y: int = obj.y
XcbRandrCrtcT = int
class XcbRandrGetCrtcInfoCookieT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.sequence: int = obj.sequence
class XcbRandrGetCrtcInfoReplyT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.height: int = obj.height
        self.length: int = obj.length
        self.mode: XcbRandrModeT = obj.mode
        self.numOutputs: int = obj.num_outputs
        self.numPossibleOutputs: int = obj.num_possible_outputs
        self.responseType: int = obj.response_type
        self.rotation: int = obj.rotation
        self.rotations: int = obj.rotations
        self.sequence: int = obj.sequence
        self.status: int = obj.status
        self.timestamp: XcbTimestampT = obj.timestamp
        self.width: int = obj.width
        self.x: XcbTimestampT = obj.x
        self.y: int = obj.y
class XcbRandrGetCrtcTransformCookieT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.sequence: int = obj.sequence
class XcbRandrGetCrtcTransformReplyT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.currentLen: int = obj.current_len
        self.currentNparams: int = obj.current_nparams
        self.currentTransform: XcbRenderTransformT = obj.current_transform
        self.hasTransforms: int = obj.has_transforms
        self.length: int = obj.length
        self.pad0: int = obj.pad0
        self.pad1: int = obj.pad1
        self.pad2: int = obj.pad2
        self.pendingLen: int = obj.pending_len
        self.pendingNparams: int = obj.pending_nparams
        self.pendingTransform: XcbRenderTransformT = obj.pending_transform
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
class XcbRandrGetScreenResourcesCookieT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.sequence: int = obj.sequence
class XcbRandrGetScreenResourcesReplyT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.configTimestamp: XcbTimestampT = obj.config_timestamp
        self.length: int = obj.length
        self.namesLen: int = obj.names_len
        self.numCrtcs: int = obj.num_crtcs
        self.numModes: int = obj.num_modes
        self.numOutputs: int = obj.num_outputs
        self.pad0: int = obj.pad0
        self.pad1: int = obj.pad1
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
        self.timestamp: XcbTimestampT = obj.timestamp
XcbRandrModeT = int
# skipping XcbRandrNotifyDataT, because its not fully defined
class XcbRandrNotifyDataT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
# skipping XcbRandrNotifyEventT, because its not fully defined
class XcbRandrNotifyEventT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
# skipping XcbRandrOutputChangeT, because its not fully defined
class XcbRandrOutputChangeT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
# skipping XcbRandrOutputPropertyT, because its not fully defined
class XcbRandrOutputPropertyT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
XcbRandrOutputT = int
class XcbRandrProviderChangeT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.pad0: int = obj.pad0
        self.provider: XcbRandrProviderT = obj.provider
        self.timestamp: XcbTimestampT = obj.timestamp
        self.window: XcbWindowT = obj.window
# skipping XcbRandrProviderPropertyT, because its not fully defined
class XcbRandrProviderPropertyT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
XcbRandrProviderT = int
class XcbRandrResourceChangeT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.pad0: int = obj.pad0
        self.timestamp: XcbTimestampT = obj.timestamp
        self.window: XcbWindowT = obj.window
class XcbRandrSetCrtcConfigCookieT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.sequence: int = obj.sequence
class XcbRandrSetCrtcConfigReplyT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.length: int = obj.length
        self.pad0: int = obj.pad0
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
        self.status: int = obj.status
        self.timestamp: XcbTimestampT = obj.timestamp
class XcbRectangleT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.height: int = obj.height
        self.width: int = obj.width
        self.x: int = obj.x
        self.y: int = obj.y
XcbRenderFixedT = int
class XcbRenderTransformT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.matrix11: XcbRenderFixedT = obj.matrix11
        self.matrix12: XcbRenderFixedT = obj.matrix12
        self.matrix13: XcbRenderFixedT = obj.matrix13
        self.matrix21: XcbRenderFixedT = obj.matrix21
        self.matrix22: XcbRenderFixedT = obj.matrix22
        self.matrix23: XcbRenderFixedT = obj.matrix23
        self.matrix31: XcbRenderFixedT = obj.matrix31
        self.matrix32: XcbRenderFixedT = obj.matrix32
        self.matrix33: XcbRenderFixedT = obj.matrix33
class XcbReparentNotifyEventT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.event: XcbWindowT = obj.event
        self.overrideRedirect: int = obj.override_redirect
        self.pad0: int = obj.pad0
        self.pad1: int = obj.pad1
        self.parent: XcbWindowT = obj.parent
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
        self.window: XcbWindowT = obj.window
        self.x: XcbWindowT = obj.x
        self.y: int = obj.y
class XcbScreenT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.allowedDepthsLen: int = obj.allowed_depths_len
        self.backingStores: int = obj.backing_stores
        self.blackPixel: int = obj.black_pixel
        self.currentInputMasks: int = obj.current_input_masks
        self.defaultColormap: XcbColormapT = obj.default_colormap
        self.heightInMillimeters: int = obj.height_in_millimeters
        self.heightInPixels: int = obj.height_in_pixels
        self.maxInstalledMaps: int = obj.max_installed_maps
        self.minInstalledMaps: int = obj.min_installed_maps
        self.root: XcbWindowT = obj.root
        self.rootDepth: int = obj.root_depth
        self.rootVisual: XcbVisualidT = obj.root_visual
        self.saveUnders: int = obj.save_unders
        self.whitePixel: int = obj.white_pixel
        self.widthInMillimeters: int = obj.width_in_millimeters
        self.widthInPixels: int = obj.width_in_pixels
class XcbSetupT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.bitmapFormatBitOrder: int = obj.bitmap_format_bit_order
        self.bitmapFormatScanlinePad: int = obj.bitmap_format_scanline_pad
        self.bitmapFormatScanlineUnit: int = obj.bitmap_format_scanline_unit
        self.imageByteOrder: int = obj.image_byte_order
        self.length: int = obj.length
        self.maxKeycode: XcbKeycodeT = obj.max_keycode
        self.maximumRequestLength: int = obj.maximum_request_length
        self.minKeycode: XcbKeycodeT = obj.min_keycode
        self.motionBufferSize: int = obj.motion_buffer_size
        self.pad0: int = obj.pad0
        self.pad1: int = obj.pad1
        self.pixmapFormatsLen: int = obj.pixmap_formats_len
        self.protocolMajorVersion: int = obj.protocol_major_version
        self.protocolMinorVersion: int = obj.protocol_minor_version
        self.releaseNumber: int = obj.release_number
        self.resourceIdBase: int = obj.resource_id_base
        self.resourceIdMask: int = obj.resource_id_mask
        self.rootsLen: int = obj.roots_len
        self.status: int = obj.status
        self.vendorLen: int = obj.vendor_len
class XcbShm(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.addr: Ptr[void] = obj.addr
        self.id: int = obj.id
class XcbShmGetImageCookieT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.sequence: int = obj.sequence
class XcbShmGetImageReplyT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.depth: int = obj.depth
        self.length: int = obj.length
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
        self.size: int = obj.size
        self.visual: XcbVisualidT = obj.visual
class XcbShmQueryVersionCookieT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.sequence: int = obj.sequence
class XcbShmQueryVersionReplyT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.gid: int = obj.gid
        self.length: int = obj.length
        self.majorVersion: int = obj.major_version
        self.minorVersion: int = obj.minor_version
        self.pad0: int = obj.pad0
        self.pixmapFormat: int = obj.pixmap_format
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
        self.sharedPixmaps: int = obj.shared_pixmaps
        self.uid: int = obj.uid
XcbShmSegT = int
XcbTimestampT = int
class XcbUnmapNotifyEventT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.event: XcbWindowT = obj.event
        self.fromConfigure: int = obj.from_configure
        self.pad0: int = obj.pad0
        self.pad1: int = obj.pad1
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
        self.window: XcbWindowT = obj.window
XcbVisualidT = int
class XcbVoidCookieT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.sequence: int = obj.sequence
XcbWindowT = int
class XcbXineramaQueryScreensCookieT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.sequence: int = obj.sequence
class XcbXineramaQueryScreensReplyT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.length: int = obj.length
        self.number: int = obj.number
        self.pad0: int = obj.pad0
        self.pad1: int = obj.pad1
        self.responseType: int = obj.response_type
        self.sequence: int = obj.sequence
class XcbXineramaScreenInfoT(Base):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()
        if obj == ffi.NULL:return
        self.height: int = obj.height
        self.width: int = obj.width
        self.xOrg: int = obj.x_org
        self.yOrg: int = obj.y_org

# funcs and vars
XCBAtomAny: int = 0
XCBAtomArc: int = 3
XCBAtomAtom: int = 4
XCBAtomBitmap: int = 5
XCBAtomCapHeight: int = 66
XCBAtomCardinal: int = 6
XCBAtomColormap: int = 7
XCBAtomCopyright: int = 61
XCBAtomCursor: int = 8
XCBAtomCutBuffer0: int = 9
XCBAtomCutBuffer1: int = 10
XCBAtomCutBuffer2: int = 11
XCBAtomCutBuffer3: int = 12
XCBAtomCutBuffer4: int = 13
XCBAtomCutBuffer5: int = 14
XCBAtomCutBuffer6: int = 15
XCBAtomCutBuffer7: int = 16
XCBAtomDrawable: int = 17
XCBAtomEndSpace: int = 46
XCBAtomFamilyName: int = 64
XCBAtomFont: int = 18
XCBAtomFontName: int = 63
XCBAtomFullName: int = 65
XCBAtomInteger: int = 19
XCBAtomItalicAngle: int = 55
XCBAtomMaxSpace: int = 45
XCBAtomMinSpace: int = 43
XCBAtomNone: int = 0
XCBAtomNormSpace: int = 44
XCBAtomNotice: int = 62
XCBAtomPixmap: int = 20
XCBAtomPoint: int = 21
XCBAtomPointSize: int = 59
XCBAtomPrimary: int = 1
XCBAtomQuadWidth: int = 57
XCBAtomRectangle: int = 22
XCBAtomResolution: int = 60
XCBAtomResourceManager: int = 23
XCBAtomRgbBestMap: int = 25
XCBAtomRgbBlueMap: int = 26
XCBAtomRgbColorMap: int = 24
XCBAtomRgbDefaultMap: int = 27
XCBAtomRgbGrayMap: int = 28
XCBAtomRgbGreenMap: int = 29
XCBAtomRgbRedMap: int = 30
XCBAtomSecondary: int = 2
XCBAtomStrikeoutAscent: int = 53
XCBAtomStrikeoutDescent: int = 54
XCBAtomString: int = 31
XCBAtomSubscriptX: int = 49
XCBAtomSubscriptY: int = 50
XCBAtomSuperscriptX: int = 47
XCBAtomSuperscriptY: int = 48
XCBAtomUnderlinePosition: int = 51
XCBAtomUnderlineThickness: int = 52
XCBAtomVisualid: int = 32
XCBAtomWeight: int = 58
XCBAtomWindow: int = 33
XCBAtomWmClass: int = 67
XCBAtomWmClientMachine: int = 36
XCBAtomWmCommand: int = 34
XCBAtomWmHints: int = 35
XCBAtomWmIconName: int = 37
XCBAtomWmIconSize: int = 38
XCBAtomWmName: int = 39
XCBAtomWmNormalHints: int = 40
XCBAtomWmSizeHints: int = 41
XCBAtomWmTransientFor: int = 68
XCBAtomWmZoomHints: int = 42
XCBAtomXHeight: int = 56
XCBButtonIndex1: int = 1
XCBButtonIndex2: int = 2
XCBButtonIndex3: int = 3
XCBButtonIndex4: int = 4
XCBButtonIndex5: int = 5
XCBButtonIndexAny: int = 0
XCBButtonPress: int = 4
XCBButtonRelease: int = 5
XCBCirculateNotify: int = 26
XCBCirculateRequest: int = 27
XCBClientMessage: int = 33
XCBColormapNotify: int = 32
XCBConfigureNotify: int = 22
XCBConfigureRequest: int = 23
XCBConfigWindowBorderWidth: int = 16
XCBConfigWindowHeight: int = 8
XCBConfigWindowSibling: int = 32
XCBConfigWindowStackMode: int = 64
XCBConfigWindowWidth: int = 4
XCBConfigWindowX: int = 1
XCBConfigWindowY: int = 2
XCBCopyFromParent: int = 0
XCBCreateNotify: int = 16
XCBCurrentTime: int = 0
XCBCwBackingPixel: int = 256
XCBCwBackingPlanes: int = 128
XCBCwBackingStore: int = 64
XCBCwBackPixel: int = 2
XCBCwBackPixmap: int = 1
XCBCwBitGravity: int = 16
XCBCwBorderPixel: int = 8
XCBCwBorderPixmap: int = 4
XCBCwColormap: int = 8192
XCBCwCursor: int = 16384
XCBCwDontPropagate: int = 4096
XCBCwEventMask: int = 2048
XCBCwOverrideRedirect: int = 512
XCBCwSaveUnder: int = 1024
XCBCwWinGravity: int = 32
XCBDestroyNotify: int = 17
XCBDpmsDpmsModeOff: int = 3
XCBDpmsDpmsModeOn: int = 0
XCBDpmsDpmsModeStandby: int = 1
XCBDpmsDpmsModeSuspend: int = 2
XCBEnterNotify: int = 7
XCBEventMaskButton1Motion: int = 256
XCBEventMaskButton2Motion: int = 512
XCBEventMaskButton3Motion: int = 1024
XCBEventMaskButton4Motion: int = 2048
XCBEventMaskButton5Motion: int = 4096
XCBEventMaskButtonMotion: int = 8192
XCBEventMaskButtonPress: int = 4
XCBEventMaskButtonRelease: int = 8
XCBEventMaskColorMapChange: int = 8388608
XCBEventMaskEnterWindow: int = 16
XCBEventMaskExposure: int = 32768
XCBEventMaskFocusChange: int = 2097152
XCBEventMaskKeymapState: int = 16384
XCBEventMaskKeyPress: int = 1
XCBEventMaskKeyRelease: int = 2
XCBEventMaskLeaveWindow: int = 32
XCBEventMaskNoEvent: int = 0
XCBEventMaskOwnerGrabButton: int = 16777216
XCBEventMaskPointerMotion: int = 64
XCBEventMaskPointerMotionHint: int = 128
XCBEventMaskPropertyChange: int = 4194304
XCBEventMaskResizeRedirect: int = 262144
XCBEventMaskStructureNotify: int = 131072
XCBEventMaskSubstructureNotify: int = 524288
XCBEventMaskSubstructureRedirect: int = 1048576
XCBEventMaskVisibilityChange: int = 65536
XCBExpose: int = 12
XCBFocusIn: int = 9
XCBFocusOut: int = 10
XCBGcArcMode: int = 4194304
XCBGcBackground: int = 8
XCBGcCapStyle: int = 64
XCBGcClipMask: int = 524288
XCBGcClipOriginX: int = 131072
XCBGcClipOriginY: int = 262144
XCBGcDashList: int = 2097152
XCBGcDashOffset: int = 1048576
XCBGcFillRule: int = 512
XCBGcFillStyle: int = 256
XCBGcFont: int = 16384
XCBGcForeground: int = 4
XCBGcFunction: int = 1
XCBGcGraphicsExposures: int = 65536
XCBGcJoinStyle: int = 128
XCBGcLineStyle: int = 32
XCBGcLineWidth: int = 16
XCBGcPlaneMask: int = 2
XCBGcStipple: int = 2048
XCBGcSubwindowMode: int = 32768
XCBGcTile: int = 1024
XCBGcTileStippleOriginX: int = 4096
XCBGcTileStippleOriginY: int = 8192
XCBGetPropertyTypeAny: int = 0
XCBGeGeneric: int = 35
XCBGrabAny: int = 0
XCBGrabModeAsync: int = 1
XCBGraphicsExposure: int = 13
XCBGravityNotify: int = 24
XCBGxAnd: int = 1
XCBGxAndInverted: int = 4
XCBGxAndReverse: int = 2
XCBGxClear: int = 0
XCBGxCopy: int = 3
XCBGxCopyInverted: int = 12
XCBGxEquiv: int = 9
XCBGxInvert: int = 10
XCBGxNand: int = 14
XCBGxNoop: int = 5
XCBGxNor: int = 8
XCBGxOr: int = 7
XCBGxOrInverted: int = 13
XCBGxOrReverse: int = 11
XCBGxSet: int = 15
XCBGxXor: int = 6
XCBIcccmWmHintIconMask: int = 32
XCBIcccmWmHintIconPixmap: int = 4
XCBIcccmWmHintIconPosition: int = 16
XCBIcccmWmHintIconWindow: int = 8
XCBIcccmWmHintInput: int = 1
XCBIcccmWmHintState: int = 2
XCBIcccmWmHintWindowGroup: int = 64
XCBIcccmWmHintXUrgency: int = 256
XCBImageFormatXyBitmap: int = 0
XCBImageFormatXyPixmap: int = 1
XCBImageFormatZPixmap: int = 2
XCBImageOrderLsbFirst: int = 0
XCBImageOrderMsbFirst: int = 1
XCBInputFocusFollowKeyboard: int = 3
XCBInputFocusNone: int = 0
XCBInputFocusParent: int = 2
XCBInputFocusPointerRoot: int = 1
XCBKeymapNotify: int = 11
XCBKeyPress: int = 2
XCBKeyRelease: int = 3
XCBLeaveNotify: int = 8
XCBLineStyleDoubleDash: int = 2
XCBLineStyleOnOffDash: int = 1
XCBLineStyleSolid: int = 0
XCBMappingNotify: int = 34
XCBMapNotify: int = 19
XCBMapRequest: int = 20
XCBMapStateUnmapped: int = 0
XCBMapStateUnviewable: int = 1
XCBMapStateViewable: int = 2
XCBModMask1: int = 8
XCBModMask2: int = 16
XCBModMask3: int = 32
XCBModMask4: int = 64
XCBModMask5: int = 128
XCBModMaskAny: int = 32768
XCBModMaskControl: int = 4
XCBModMaskLock: int = 2
XCBModMaskShift: int = 1
XCBMotionNotify: int = 6
XCBNone: int = 0
XCBNoExposure: int = 14
XCBPropertyNotify: int = 28
XCBPropModeAppend: int = 2
XCBPropModePrepend: int = 1
XCBPropModeReplace: int = 0
XCBRandrNotify: int = 1
XCBRandrNotifyCrtcChange: int = 0
XCBRandrNotifyMaskCrtcChange: int = 2
XCBRandrNotifyMaskOutputChange: int = 4
XCBRandrNotifyMaskOutputProperty: int = 8
XCBRandrNotifyMaskProviderChange: int = 16
XCBRandrNotifyMaskProviderProperty: int = 32
XCBRandrNotifyMaskResourceChange: int = 64
XCBRandrNotifyMaskScreenChange: int = 1
XCBRandrNotifyOutputChange: int = 1
XCBRandrNotifyOutputProperty: int = 2
XCBRandrNotifyProviderChange: int = 3
XCBRandrNotifyProviderProperty: int = 4
XCBRandrNotifyResourceChange: int = 5
XCBReparentNotify: int = 21
XCBResizeRequest: int = 25
XCBSelectionClear: int = 29
XCBSelectionNotify: int = 31
XCBSelectionRequest: int = 30
XCBSendEventDestItemFocus: int = 1
XCBSendEventDestPointerWindow: int = 0
XCBStackModeAbove: int = 0
XCBStackModeBelow: int = 1
XCBStackModeBottomIf: int = 3
XCBStackModeOpposite: int = 4
XCBStackModeTopIf: int = 2
XCBUnmapNotify: int = 18
XCBVisibilityNotify: int = 15
XCBWindowClassCopyFromParent: int = 0
XCBWindowClassInputOnly: int = 2
XCBWindowClassInputOutput: int = 1
XCBWindowNone: int = 0

def createShm(conn: CPtr[XcbConnectionT], size: int, ) -> 'XcbShm':return XcbShm(lib.create_shm(*parseArgs(conn, size, )))
def doubleToFixed(n: float, ) -> int:return int(lib.double_to_fixed(*parseArgs(n, )))
def removeShm(conn: CPtr[XcbConnectionT], shm: 'XcbShm', ) -> void:return void(lib.remove_shm(*parseArgs(conn, shm, )))
def xcbAuxGetScreen(conn: CPtr[XcbConnectionT], screen: int, ) -> CPtr[XcbScreenT]:return XcbScreenT(lib.xcb_aux_get_screen(*parseArgs(conn, screen, )))
def xcbChangeProperty(conn: CPtr[XcbConnectionT], mode: int, window: int, property: int, type: int, format: int, dataLen: int, data: Ptr[void], ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_change_property(*parseArgs(conn, mode, window, property, type, format, dataLen, data, )))
def xcbChangeWindowAttributesChecked(conn: CPtr[XcbConnectionT], window: int, valueMask: int, valueList: Ptr[void], ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_change_window_attributes_checked(*parseArgs(conn, window, valueMask, valueList, )))
def xcbCloseFont(conn: CPtr[XcbConnectionT], font: int, ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_close_font(*parseArgs(conn, font, )))
def xcbConfigureWindow(conn: CPtr[XcbConnectionT], window: int, valueMask: int, valueList: Ptr[void], ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_configure_window(*parseArgs(conn, window, valueMask, valueList, )))
def xcbConnect(displayname: Ptr[int], screenp: Ptr[int], ) -> CPtr[XcbConnectionT]:return XcbConnectionT(lib.xcb_connect(*parseArgs(displayname, screenp, )))
def xcbConnectionHasError(conn: CPtr[XcbConnectionT], ) -> int:return int(lib.xcb_connection_has_error(*parseArgs(conn, )))
def xcbCopyArea(conn: CPtr[XcbConnectionT], srcDrawable: int, dstDrawable: int, gc: int, srcX: int, srcY: int, dstX: int, dstY: int, width: int, height: int, ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_copy_area(*parseArgs(conn, srcDrawable, dstDrawable, gc, srcX, srcY, dstX, dstY, width, height, )))
def xcbCreateGc(conn: CPtr[XcbConnectionT], cid: int, drawable: int, valueMask: int, valueList: Ptr[void], ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_create_gc(*parseArgs(conn, cid, drawable, valueMask, valueList, )))
def xcbCreateGlyphCursor(conn: CPtr[XcbConnectionT], cid: int, sourceFont: int, maskFont: int, sourceChar: int, maskChar: int, foreRed: int, foreGreen: int, foreBlue: int, backRed: int, backGreen: int, backBlue: int, ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_create_glyph_cursor(*parseArgs(conn, cid, sourceFont, maskFont, sourceChar, maskChar, foreRed, foreGreen, foreBlue, backRed, backGreen, backBlue, )))
def xcbCreatePixmap(conn: CPtr[XcbConnectionT], depth: int, pid: int, drawable: int, width: int, height: int, ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_create_pixmap(*parseArgs(conn, depth, pid, drawable, width, height, )))
def xcbCreateWindow(conn: CPtr[XcbConnectionT], depth: int, wid: int, parent: int, x: int, y: int, width: int, height: int, borderWidth: int, Class: int, visual: int, valueMask: int, valueList: Ptr[void], ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_create_window(*parseArgs(conn, depth, wid, parent, x, y, width, height, borderWidth, Class, visual, valueMask, valueList, )))
def xcbDeleteProperty(conn: CPtr[XcbConnectionT], window: int, property: int, ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_delete_property(*parseArgs(conn, window, property, )))
def xcbDestroyWindow(conn: CPtr[XcbConnectionT], window: int, ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_destroy_window(*parseArgs(conn, window, )))
def xcbDisconnect(conn: CPtr[XcbConnectionT], ) -> void:return void(lib.xcb_disconnect(*parseArgs(conn, )))
def xcbDpmsCapableReply(conn: CPtr[XcbConnectionT], cookie: 'XcbDpmsCapableCookieT', e: CPtr[XcbGenericErrorT], ) -> CPtr[XcbDpmsCapableReplyT]:return XcbDpmsCapableReplyT(lib.xcb_dpms_capable_reply(*parseArgs(conn, cookie, e, )))
def xcbDpmsCapableUnchecked(conn: CPtr[XcbConnectionT], ) -> 'XcbDpmsCapableCookieT':return XcbDpmsCapableCookieT(lib.xcb_dpms_capable_unchecked(*parseArgs(conn, )))
def xcbDpmsDisable(conn: CPtr[XcbConnectionT], ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_dpms_disable(*parseArgs(conn, )))
def xcbDpmsEnable(conn: CPtr[XcbConnectionT], ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_dpms_enable(*parseArgs(conn, )))
def xcbDpmsForceLevel(conn: CPtr[XcbConnectionT], powerLevel: int, ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_dpms_force_level(*parseArgs(conn, powerLevel, )))
def xcbDpmsGetTimeoutsReply(conn: CPtr[XcbConnectionT], cookie: 'XcbDpmsGetTimeoutsCookieT', e: CPtr[XcbGenericErrorT], ) -> CPtr[XcbDpmsGetTimeoutsReplyT]:return XcbDpmsGetTimeoutsReplyT(lib.xcb_dpms_get_timeouts_reply(*parseArgs(conn, cookie, e, )))
def xcbDpmsGetTimeoutsUnchecked(conn: CPtr[XcbConnectionT], ) -> 'XcbDpmsGetTimeoutsCookieT':return XcbDpmsGetTimeoutsCookieT(lib.xcb_dpms_get_timeouts_unchecked(*parseArgs(conn, )))
def xcbDpmsInfoReply(conn: CPtr[XcbConnectionT], cookie: 'XcbDpmsInfoCookieT', e: CPtr[XcbGenericErrorT], ) -> CPtr[XcbDpmsInfoReplyT]:return XcbDpmsInfoReplyT(lib.xcb_dpms_info_reply(*parseArgs(conn, cookie, e, )))
def xcbDpmsInfoUnchecked(conn: CPtr[XcbConnectionT], ) -> 'XcbDpmsInfoCookieT':return XcbDpmsInfoCookieT(lib.xcb_dpms_info_unchecked(*parseArgs(conn, )))
def xcbDpmsSetTimeouts(conn: CPtr[XcbConnectionT], standbyTimeout: int, suspendTimeout: int, offTimeout: int, ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_dpms_set_timeouts(*parseArgs(conn, standbyTimeout, suspendTimeout, offTimeout, )))
def xcbErrorsContextFree(ctx: CPtr[XcbErrorsContextT], ) -> void:return void(lib.xcb_errors_context_free(*parseArgs(ctx, )))
def xcbErrorsContextNew(conn: CPtr[XcbConnectionT], c: CPtr[XcbErrorsContextT], ) -> int:return int(lib.xcb_errors_context_new(*parseArgs(conn, c, )))
def xcbErrorsGetNameForError(ctx: CPtr[XcbErrorsContextT], errorCode: int, extension: Ptr[int], ) -> Ptr[int]:return Ptr(lib.xcb_errors_get_name_for_error(*parseArgs(ctx, errorCode, extension, )))
def xcbErrorsGetNameForMajorCode(ctx: CPtr[XcbErrorsContextT], majorCode: int, ) -> Ptr[int]:return Ptr(lib.xcb_errors_get_name_for_major_code(*parseArgs(ctx, majorCode, )))
def xcbErrorsGetNameForMinorCode(ctx: CPtr[XcbErrorsContextT], majorCode: int, minorCode: int, ) -> Ptr[int]:return Ptr(lib.xcb_errors_get_name_for_minor_code(*parseArgs(ctx, majorCode, minorCode, )))
def xcbFlush(conn: CPtr[XcbConnectionT], ) -> int:return int(lib.xcb_flush(*parseArgs(conn, )))
def xcbFreeCursor(conn: CPtr[XcbConnectionT], cursor: int, ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_free_cursor(*parseArgs(conn, cursor, )))
def xcbFreePixmap(conn: CPtr[XcbConnectionT], pixmap: int, ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_free_pixmap(*parseArgs(conn, pixmap, )))
def xcbGenerateId(conn: CPtr[XcbConnectionT], ) -> int:return int(lib.xcb_generate_id(*parseArgs(conn, )))
def xcbGetAtomName(conn: CPtr[XcbConnectionT], atom: int, ) -> 'XcbGetAtomNameCookieT':return XcbGetAtomNameCookieT(lib.xcb_get_atom_name(*parseArgs(conn, atom, )))
def xcbGetAtomNameName(R: CPtr[XcbGetAtomNameReplyT], ) -> Ptr[int]:return Ptr(lib.xcb_get_atom_name_name(*parseArgs(R, )))
def xcbGetAtomNameReply(conn: CPtr[XcbConnectionT], cookie: 'XcbGetAtomNameCookieT', e: CPtr[XcbGenericErrorT], ) -> CPtr[XcbGetAtomNameReplyT]:return XcbGetAtomNameReplyT(lib.xcb_get_atom_name_reply(*parseArgs(conn, cookie, e, )))
def xcbGetExtensionData(conn: CPtr[XcbConnectionT], ext: CPtr[XcbExtensionT], ) -> CPtr[XcbQueryExtensionReplyT]:return XcbQueryExtensionReplyT(lib.xcb_get_extension_data(*parseArgs(conn, ext, )))
def xcbGetFileDescriptor(conn: CPtr[XcbConnectionT], ) -> int:return int(lib.xcb_get_file_descriptor(*parseArgs(conn, )))
def xcbGetGeometry(conn: CPtr[XcbConnectionT], drawable: int, ) -> 'XcbGetGeometryCookieT':return XcbGetGeometryCookieT(lib.xcb_get_geometry(*parseArgs(conn, drawable, )))
def xcbGetGeometryReply(conn: CPtr[XcbConnectionT], cookie: 'XcbGetGeometryCookieT', e: CPtr[XcbGenericErrorT], ) -> CPtr[XcbGetGeometryReplyT]:return XcbGetGeometryReplyT(lib.xcb_get_geometry_reply(*parseArgs(conn, cookie, e, )))
def xcbGetImage(conn: CPtr[XcbConnectionT], format: int, drawable: int, x: int, y: int, width: int, height: int, planeMask: int, ) -> 'XcbGetImageCookieT':return XcbGetImageCookieT(lib.xcb_get_image(*parseArgs(conn, format, drawable, x, y, width, height, planeMask, )))
def xcbGetImageData(R: CPtr[XcbGetImageReplyT], ) -> Ptr[int]:return Ptr(lib.xcb_get_image_data(*parseArgs(R, )))
def xcbGetImageDataLength(R: CPtr[XcbGetImageReplyT], ) -> int:return int(lib.xcb_get_image_data_length(*parseArgs(R, )))
def xcbGetImageReply(conn: CPtr[XcbConnectionT], cookie: 'XcbGetImageCookieT', e: CPtr[XcbGenericErrorT], ) -> CPtr[XcbGetImageReplyT]:return XcbGetImageReplyT(lib.xcb_get_image_reply(*parseArgs(conn, cookie, e, )))
def xcbGetKeyboardMapping(conn: CPtr[XcbConnectionT], firstKeycode: int, count: int, ) -> 'XcbGetKeyboardMappingCookieT':return XcbGetKeyboardMappingCookieT(lib.xcb_get_keyboard_mapping(*parseArgs(conn, firstKeycode, count, )))
def xcbGetKeyboardMappingReply(conn: CPtr[XcbConnectionT], cookie: 'XcbGetKeyboardMappingCookieT', e: CPtr[XcbGenericErrorT], ) -> CPtr[XcbGetKeyboardMappingReplyT]:return XcbGetKeyboardMappingReplyT(lib.xcb_get_keyboard_mapping_reply(*parseArgs(conn, cookie, e, )))
def xcbGetMaximumRequestLength(conn: CPtr[XcbConnectionT], ) -> int:return int(lib.xcb_get_maximum_request_length(*parseArgs(conn, )))
def xcbGetModifierMappingKeycodes(R: CPtr[XcbGetModifierMappingReplyT], ) -> Ptr[int]:return Ptr(lib.xcb_get_modifier_mapping_keycodes(*parseArgs(R, )))
def xcbGetModifierMappingReply(conn: CPtr[XcbConnectionT], cookie: 'XcbGetModifierMappingCookieT', e: CPtr[XcbGenericErrorT], ) -> CPtr[XcbGetModifierMappingReplyT]:return XcbGetModifierMappingReplyT(lib.xcb_get_modifier_mapping_reply(*parseArgs(conn, cookie, e, )))
def xcbGetModifierMappingUnchecked(conn: CPtr[XcbConnectionT], ) -> 'XcbGetModifierMappingCookieT':return XcbGetModifierMappingCookieT(lib.xcb_get_modifier_mapping_unchecked(*parseArgs(conn, )))
def xcbGetProperty(conn: CPtr[XcbConnectionT], Delete: int, window: int, property: int, type: int, longOffset: int, longLength: int, ) -> 'XcbGetPropertyCookieT':return XcbGetPropertyCookieT(lib.xcb_get_property(*parseArgs(conn, Delete, window, property, type, longOffset, longLength, )))
def xcbGetPropertyReply(conn: CPtr[XcbConnectionT], cookie: 'XcbGetPropertyCookieT', e: CPtr[XcbGenericErrorT], ) -> CPtr[XcbGetPropertyReplyT]:return XcbGetPropertyReplyT(lib.xcb_get_property_reply(*parseArgs(conn, cookie, e, )))
def xcbGetPropertyValue(reply: CPtr[XcbGetPropertyReplyT], ) -> Ptr[void]:return Ptr(lib.xcb_get_property_value(*parseArgs(reply, )))
def xcbGetPropertyValueLength(reply: CPtr[XcbGetPropertyReplyT], ) -> int:return int(lib.xcb_get_property_value_length(*parseArgs(reply, )))
def xcbGetSetup(conn: CPtr[XcbConnectionT], ) -> CPtr[XcbSetupT]:return XcbSetupT(lib.xcb_get_setup(*parseArgs(conn, )))
def xcbGetWindowAttributes(conn: CPtr[XcbConnectionT], window: int, ) -> 'XcbGetWindowAttributesCookieT':return XcbGetWindowAttributesCookieT(lib.xcb_get_window_attributes(*parseArgs(conn, window, )))
def xcbGetWindowAttributesReply(conn: CPtr[XcbConnectionT], cookie: 'XcbGetWindowAttributesCookieT', e: CPtr[XcbGenericErrorT], ) -> CPtr[XcbGetWindowAttributesReplyT]:return XcbGetWindowAttributesReplyT(lib.xcb_get_window_attributes_reply(*parseArgs(conn, cookie, e, )))
def xcbGrabButton(conn: CPtr[XcbConnectionT], ownerEvents: int, grabWindow: int, eventMask: int, pointerMode: int, keyboardMode: int, confineTo: int, cursor: int, button: int, modifiers: int, ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_grab_button(*parseArgs(conn, ownerEvents, grabWindow, eventMask, pointerMode, keyboardMode, confineTo, cursor, button, modifiers, )))
def xcbGrabKey(conn: CPtr[XcbConnectionT], ownerEvents: int, grabWindow: int, modifiers: int, key: int, pointerMode: int, keyboardMode: int, ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_grab_key(*parseArgs(conn, ownerEvents, grabWindow, modifiers, key, pointerMode, keyboardMode, )))
def xcbImageCreateNative(conn: CPtr[XcbConnectionT], width: int, height: int, format: 'XcbImageFormatT', depth: int, base: Ptr[void], bytes: int, data: Ptr[int], ) -> CPtr[XcbImageT]:return XcbImageT(lib.xcb_image_create_native(*parseArgs(conn, width, height, format, depth, base, bytes, data, )))
def xcbImageDestroy(image: CPtr[XcbImageT], ) -> void:return void(lib.xcb_image_destroy(*parseArgs(image, )))
def xcbImagePut(conn: CPtr[XcbConnectionT], draw: int, gc: int, image: CPtr[XcbImageT], x: int, y: int, leftPad: int, ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_image_put(*parseArgs(conn, draw, gc, image, x, y, leftPad, )))
def xcbImageText8(conn: CPtr[XcbConnectionT], stringLen: int, drawable: int, gc: int, x: int, y: int, string: Ptr[int], ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_image_text_8(*parseArgs(conn, stringLen, drawable, gc, x, y, string, )))
def xcbInternAtom(conn: CPtr[XcbConnectionT], onlyIfExists: int, nameLen: int, name: Ptr[int], ) -> 'XcbInternAtomCookieT':return XcbInternAtomCookieT(lib.xcb_intern_atom(*parseArgs(conn, onlyIfExists, nameLen, name, )))
def xcbInternAtomReply(conn: CPtr[XcbConnectionT], cookie: 'XcbInternAtomCookieT', e: CPtr[XcbGenericErrorT], ) -> CPtr[XcbInternAtomReplyT]:return XcbInternAtomReplyT(lib.xcb_intern_atom_reply(*parseArgs(conn, cookie, e, )))
def xcbKeySymbolsAlloc(conn: CPtr[XcbConnectionT], ) -> CPtr[Xcbkeysymbols]:return Xcbkeysymbols(lib.xcb_key_symbols_alloc(*parseArgs(conn, )))
def xcbKeySymbolsFree(syms: CPtr[Xcbkeysymbols], ) -> void:return void(lib.xcb_key_symbols_free(*parseArgs(syms, )))
def xcbKeySymbolsGetKeycode(syms: CPtr[Xcbkeysymbols], keysym: int, ) -> Ptr[int]:return Ptr(lib.xcb_key_symbols_get_keycode(*parseArgs(syms, keysym, )))
def xcbKillClient(conn: CPtr[XcbConnectionT], resource: int, ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_kill_client(*parseArgs(conn, resource, )))
def xcbMapWindow(conn: CPtr[XcbConnectionT], window: int, ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_map_window(*parseArgs(conn, window, )))
def xcbOpenFont(conn: CPtr[XcbConnectionT], fid: int, nameLen: int, name: Ptr[int], ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_open_font(*parseArgs(conn, fid, nameLen, name, )))
def xcbPollForEvent(conn: CPtr[XcbConnectionT], ) -> CPtr[XcbGenericEventT]:return XcbGenericEventT(lib.xcb_poll_for_event(*parseArgs(conn, )))
def xcbPolyFillRectangle(conn: CPtr[XcbConnectionT], drawable: int, gc: int, rectanglesLen: int, rectangles: CPtr[XcbRectangleT], ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_poly_fill_rectangle(*parseArgs(conn, drawable, gc, rectanglesLen, rectangles, )))
def xcbQueryExtensionReply(conn: CPtr[XcbConnectionT], cookie: 'XcbQueryExtensionCookieT', e: CPtr[XcbGenericErrorT], ) -> CPtr[XcbQueryExtensionReplyT]:return XcbQueryExtensionReplyT(lib.xcb_query_extension_reply(*parseArgs(conn, cookie, e, )))
def xcbQueryExtensionUnchecked(conn: CPtr[XcbConnectionT], nameLen: int, name: Ptr[int], ) -> 'XcbQueryExtensionCookieT':return XcbQueryExtensionCookieT(lib.xcb_query_extension_unchecked(*parseArgs(conn, nameLen, name, )))
def xcbQueryPointer(conn: CPtr[XcbConnectionT], window: int, ) -> 'XcbQueryPointerCookieT':return XcbQueryPointerCookieT(lib.xcb_query_pointer(*parseArgs(conn, window, )))
def xcbQueryPointerReply(conn: CPtr[XcbConnectionT], cookie: 'XcbQueryPointerCookieT', e: CPtr[XcbGenericErrorT], ) -> CPtr[XcbQueryPointerReplyT]:return XcbQueryPointerReplyT(lib.xcb_query_pointer_reply(*parseArgs(conn, cookie, e, )))
def xcbQueryTree(conn: CPtr[XcbConnectionT], window: int, ) -> 'XcbQueryTreeCookieT':return XcbQueryTreeCookieT(lib.xcb_query_tree(*parseArgs(conn, window, )))
def xcbQueryTreeChildren(reply: CPtr[XcbQueryTreeReplyT], ) -> Ptr[int]:return Ptr(lib.xcb_query_tree_children(*parseArgs(reply, )))
def xcbQueryTreeReply(conn: CPtr[XcbConnectionT], cookie: 'XcbQueryTreeCookieT', e: CPtr[XcbGenericErrorT], ) -> CPtr[XcbQueryTreeReplyT]:return XcbQueryTreeReplyT(lib.xcb_query_tree_reply(*parseArgs(conn, cookie, e, )))
def xcbRandrGetCrtcInfo(conn: CPtr[XcbConnectionT], crtc: int, configTimestamp: int, ) -> 'XcbRandrGetCrtcInfoCookieT':return XcbRandrGetCrtcInfoCookieT(lib.xcb_randr_get_crtc_info(*parseArgs(conn, crtc, configTimestamp, )))
def xcbRandrGetCrtcInfoOutputs(R: CPtr[XcbRandrGetCrtcInfoReplyT], ) -> Ptr[int]:return Ptr(lib.xcb_randr_get_crtc_info_outputs(*parseArgs(R, )))
def xcbRandrGetCrtcInfoReply(conn: CPtr[XcbConnectionT], cookie: 'XcbRandrGetCrtcInfoCookieT', e: CPtr[XcbGenericErrorT], ) -> CPtr[XcbRandrGetCrtcInfoReplyT]:return XcbRandrGetCrtcInfoReplyT(lib.xcb_randr_get_crtc_info_reply(*parseArgs(conn, cookie, e, )))
def xcbRandrGetCrtcTransform(conn: CPtr[XcbConnectionT], crtc: int, ) -> 'XcbRandrGetCrtcTransformCookieT':return XcbRandrGetCrtcTransformCookieT(lib.xcb_randr_get_crtc_transform(*parseArgs(conn, crtc, )))
def xcbRandrGetCrtcTransformReply(conn: CPtr[XcbConnectionT], cookie: 'XcbRandrGetCrtcTransformCookieT', e: CPtr[XcbGenericErrorT], ) -> CPtr[XcbRandrGetCrtcTransformReplyT]:return XcbRandrGetCrtcTransformReplyT(lib.xcb_randr_get_crtc_transform_reply(*parseArgs(conn, cookie, e, )))
def xcbRandrGetScreenResources(conn: CPtr[XcbConnectionT], window: int, ) -> 'XcbRandrGetScreenResourcesCookieT':return XcbRandrGetScreenResourcesCookieT(lib.xcb_randr_get_screen_resources(*parseArgs(conn, window, )))
def xcbRandrGetScreenResourcesCrtcs(R: CPtr[XcbRandrGetScreenResourcesReplyT], ) -> Ptr[int]:return Ptr(lib.xcb_randr_get_screen_resources_crtcs(*parseArgs(R, )))
def xcbRandrGetScreenResourcesCrtcsLength(R: CPtr[XcbRandrGetScreenResourcesReplyT], ) -> int:return int(lib.xcb_randr_get_screen_resources_crtcs_length(*parseArgs(R, )))
def xcbRandrGetScreenResourcesReply(conn: CPtr[XcbConnectionT], cookie: 'XcbRandrGetScreenResourcesCookieT', e: CPtr[XcbGenericErrorT], ) -> CPtr[XcbRandrGetScreenResourcesReplyT]:return XcbRandrGetScreenResourcesReplyT(lib.xcb_randr_get_screen_resources_reply(*parseArgs(conn, cookie, e, )))
def xcbRandrSelectInput(conn: CPtr[XcbConnectionT], window: int, enable: int, ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_randr_select_input(*parseArgs(conn, window, enable, )))
def xcbRandrSetCrtcConfig(conn: CPtr[XcbConnectionT], crtc: int, timestamp: int, configTimestamp: int, x: int, y: int, mode: int, rotation: int, outputsLen: int, outputs: Ptr[int], ) -> 'XcbRandrSetCrtcConfigCookieT':return XcbRandrSetCrtcConfigCookieT(lib.xcb_randr_set_crtc_config(*parseArgs(conn, crtc, timestamp, configTimestamp, x, y, mode, rotation, outputsLen, outputs, )))
def xcbRandrSetCrtcConfigReply(conn: CPtr[XcbConnectionT], cookie: 'XcbRandrSetCrtcConfigCookieT', e: CPtr[XcbGenericErrorT], ) -> CPtr[XcbRandrSetCrtcConfigReplyT]:return XcbRandrSetCrtcConfigReplyT(lib.xcb_randr_set_crtc_config_reply(*parseArgs(conn, cookie, e, )))
def xcbRandrSetCrtcTransform(c: CPtr[XcbConnectionT], crtc: int, transform: 'XcbRenderTransformT', filterLen: int, filterName: Ptr[int], filterParamsLen: int, filterParams: Ptr[int], ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_randr_set_crtc_transform(*parseArgs(c, crtc, transform, filterLen, filterName, filterParamsLen, filterParams, )))
def xcbReparentWindow(conn: CPtr[XcbConnectionT], window: int, parent: int, x: int, y: int, ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_reparent_window(*parseArgs(conn, window, parent, x, y, )))
def xcbSendEvent(conn: CPtr[XcbConnectionT], propagate: bool, destination: int, eventMask: int, event: Ptr[int], ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_send_event(*parseArgs(conn, propagate, destination, eventMask, event, )))
def xcbSetInputFocus(conn: CPtr[XcbConnectionT], revertTo: int, focus: int, time: int, ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_set_input_focus(*parseArgs(conn, revertTo, focus, time, )))
def xcbShmCreatePixmap(conn: CPtr[XcbConnectionT], pid: int, drawable: int, width: int, height: int, depth: int, shmseg: int, offset: int, ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_shm_create_pixmap(*parseArgs(conn, pid, drawable, width, height, depth, shmseg, offset, )))
def xcbShmGetImageReply(conn: CPtr[XcbConnectionT], cookie: 'XcbShmGetImageCookieT', e: CPtr[XcbGenericErrorT], ) -> CPtr[XcbShmGetImageReplyT]:return XcbShmGetImageReplyT(lib.xcb_shm_get_image_reply(*parseArgs(conn, cookie, e, )))
def xcbShmGetImageUnchecked(conn: CPtr[XcbConnectionT], drawable: int, x: int, y: int, width: int, height: int, planeMask: int, format: int, shmseg: int, offset: int, ) -> 'XcbShmGetImageCookieT':return XcbShmGetImageCookieT(lib.xcb_shm_get_image_unchecked(*parseArgs(conn, drawable, x, y, width, height, planeMask, format, shmseg, offset, )))
def xcbShmPutImage(conn: CPtr[XcbConnectionT], drawable: int, gc: int, totalWidth: int, totalHeight: int, srcX: int, srcY: int, srcWidth: int, srcHeight: int, dstX: int, dstY: int, depth: int, format: int, sendEvent: int, shmseg: int, offset: int, ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_shm_put_image(*parseArgs(conn, drawable, gc, totalWidth, totalHeight, srcX, srcY, srcWidth, srcHeight, dstX, dstY, depth, format, sendEvent, shmseg, offset, )))
def xcbShmQueryVersion(conn: CPtr[XcbConnectionT], ) -> 'XcbShmQueryVersionCookieT':return XcbShmQueryVersionCookieT(lib.xcb_shm_query_version(*parseArgs(conn, )))
def xcbShmQueryVersionReply(conn: CPtr[XcbConnectionT], cookie: 'XcbShmQueryVersionCookieT', e: CPtr[XcbGenericErrorT], ) -> CPtr[XcbShmQueryVersionReplyT]:return XcbShmQueryVersionReplyT(lib.xcb_shm_query_version_reply(*parseArgs(conn, cookie, e, )))
def xcbTestFakeInput(conn: CPtr[XcbConnectionT], type: int, detail: int, time: int, root: int, rootX: int, rootY: int, deviceid: int, ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_test_fake_input(*parseArgs(conn, type, detail, time, root, rootX, rootY, deviceid, )))
def xcbUngrabButton(conn: CPtr[XcbConnectionT], button: int, grabWindow: int, modifiers: int, ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_ungrab_button(*parseArgs(conn, button, grabWindow, modifiers, )))
def xcbUngrabKey(conn: CPtr[XcbConnectionT], key: int, grabWindow: int, modifiers: int, ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_ungrab_key(*parseArgs(conn, key, grabWindow, modifiers, )))
def xcbUnmapWindow(conn: CPtr[XcbConnectionT], window: int, ) -> 'XcbVoidCookieT':return XcbVoidCookieT(lib.xcb_unmap_window(*parseArgs(conn, window, )))
def xcbWaitForEvent(conn: CPtr[XcbConnectionT], ) -> CPtr[XcbGenericEventT]:return XcbGenericEventT(lib.xcb_wait_for_event(*parseArgs(conn, )))
def xcbXineramaQueryScreens(conn: CPtr[XcbConnectionT], ) -> 'XcbXineramaQueryScreensCookieT':return XcbXineramaQueryScreensCookieT(lib.xcb_xinerama_query_screens(*parseArgs(conn, )))
def xcbXineramaQueryScreensReply(conn: CPtr[XcbConnectionT], cookie: 'XcbXineramaQueryScreensCookieT', e: CPtr[XcbGenericErrorT], ) -> CPtr[XcbXineramaQueryScreensReplyT]:return XcbXineramaQueryScreensReplyT(lib.xcb_xinerama_query_screens_reply(*parseArgs(conn, cookie, e, )))
def xcbXineramaQueryScreensScreenInfo(R: CPtr[XcbXineramaQueryScreensReplyT], ) -> CPtr[XcbXineramaScreenInfoT]:return XcbXineramaScreenInfoT(lib.xcb_xinerama_query_screens_screen_info(*parseArgs(R, )))
type XcbAtomEnumT = Literal['XCBAtomNone', 'XCBAtomAny', 'XCBAtomPrimary', 'XCBAtomSecondary', 'XCBAtomArc', 'XCBAtomAtom', 'XCBAtomBitmap', 'XCBAtomCardinal', 'XCBAtomColormap', 'XCBAtomCursor', 'XCBAtomCutBuffer0', 'XCBAtomCutBuffer1', 'XCBAtomCutBuffer2', 'XCBAtomCutBuffer3', 'XCBAtomCutBuffer4', 'XCBAtomCutBuffer5', 'XCBAtomCutBuffer6', 'XCBAtomCutBuffer7', 'XCBAtomDrawable', 'XCBAtomFont', 'XCBAtomInteger', 'XCBAtomPixmap', 'XCBAtomPoint', 'XCBAtomRectangle', 'XCBAtomResourceManager', 'XCBAtomRgbColorMap', 'XCBAtomRgbBestMap', 'XCBAtomRgbBlueMap', 'XCBAtomRgbDefaultMap', 'XCBAtomRgbGrayMap', 'XCBAtomRgbGreenMap', 'XCBAtomRgbRedMap', 'XCBAtomString', 'XCBAtomVisualid', 'XCBAtomWindow', 'XCBAtomWmCommand', 'XCBAtomWmHints', 'XCBAtomWmClientMachine', 'XCBAtomWmIconName', 'XCBAtomWmIconSize', 'XCBAtomWmName', 'XCBAtomWmNormalHints', 'XCBAtomWmSizeHints', 'XCBAtomWmZoomHints', 'XCBAtomMinSpace', 'XCBAtomNormSpace', 'XCBAtomMaxSpace', 'XCBAtomEndSpace', 'XCBAtomSuperscriptX', 'XCBAtomSuperscriptY', 'XCBAtomSubscriptX', 'XCBAtomSubscriptY', 'XCBAtomUnderlinePosition', 'XCBAtomUnderlineThickness', 'XCBAtomStrikeoutAscent', 'XCBAtomStrikeoutDescent', 'XCBAtomItalicAngle', 'XCBAtomXHeight', 'XCBAtomQuadWidth', 'XCBAtomWeight', 'XCBAtomPointSize', 'XCBAtomResolution', 'XCBAtomCopyright', 'XCBAtomNotice', 'XCBAtomFontName', 'XCBAtomFamilyName', 'XCBAtomFullName', 'XCBAtomCapHeight', 'XCBAtomWmClass', 'XCBAtomWmTransientFor']
type XcbButtonIndexT = Literal['XCBButtonIndexAny', 'XCBButtonIndex1', 'XCBButtonIndex2', 'XCBButtonIndex3', 'XCBButtonIndex4', 'XCBButtonIndex5']
type XcbConfigWindowT = Literal['XCBConfigWindowX', 'XCBConfigWindowY', 'XCBConfigWindowWidth', 'XCBConfigWindowHeight', 'XCBConfigWindowBorderWidth', 'XCBConfigWindowSibling', 'XCBConfigWindowStackMode']
type XcbCwT = Literal['XCBCwBackPixmap', 'XCBCwBackPixel', 'XCBCwBorderPixmap', 'XCBCwBorderPixel', 'XCBCwBitGravity', 'XCBCwWinGravity', 'XCBCwBackingStore', 'XCBCwBackingPlanes', 'XCBCwBackingPixel', 'XCBCwOverrideRedirect', 'XCBCwSaveUnder', 'XCBCwEventMask', 'XCBCwDontPropagate', 'XCBCwColormap', 'XCBCwCursor']
type XcbDpmsDpmsModeT = Literal['XCBDpmsDpmsModeOn', 'XCBDpmsDpmsModeStandby', 'XCBDpmsDpmsModeSuspend', 'XCBDpmsDpmsModeOff']
type XcbEventMaskT = Literal['XCBEventMaskNoEvent', 'XCBEventMaskKeyPress', 'XCBEventMaskKeyRelease', 'XCBEventMaskButtonPress', 'XCBEventMaskButtonRelease', 'XCBEventMaskEnterWindow', 'XCBEventMaskLeaveWindow', 'XCBEventMaskPointerMotion', 'XCBEventMaskPointerMotionHint', 'XCBEventMaskButton1Motion', 'XCBEventMaskButton2Motion', 'XCBEventMaskButton3Motion', 'XCBEventMaskButton4Motion', 'XCBEventMaskButton5Motion', 'XCBEventMaskButtonMotion', 'XCBEventMaskKeymapState', 'XCBEventMaskExposure', 'XCBEventMaskVisibilityChange', 'XCBEventMaskStructureNotify', 'XCBEventMaskResizeRedirect', 'XCBEventMaskSubstructureNotify', 'XCBEventMaskSubstructureRedirect', 'XCBEventMaskFocusChange', 'XCBEventMaskPropertyChange', 'XCBEventMaskColorMapChange', 'XCBEventMaskOwnerGrabButton']
type XcbGcT = Literal['XCBGcFunction', 'XCBGcPlaneMask', 'XCBGcForeground', 'XCBGcBackground', 'XCBGcLineWidth', 'XCBGcLineStyle', 'XCBGcCapStyle', 'XCBGcJoinStyle', 'XCBGcFillStyle', 'XCBGcFillRule', 'XCBGcTile', 'XCBGcStipple', 'XCBGcTileStippleOriginX', 'XCBGcTileStippleOriginY', 'XCBGcFont', 'XCBGcSubwindowMode', 'XCBGcGraphicsExposures', 'XCBGcClipOriginX', 'XCBGcClipOriginY', 'XCBGcClipMask', 'XCBGcDashOffset', 'XCBGcDashList', 'XCBGcArcMode']
type XcbGetPropertyTypeT = Literal['XCBGetPropertyTypeAny']
type XcbGxT = Literal['XCBGxClear', 'XCBGxAnd', 'XCBGxAndReverse', 'XCBGxCopy', 'XCBGxAndInverted', 'XCBGxNoop', 'XCBGxXor', 'XCBGxOr', 'XCBGxNor', 'XCBGxEquiv', 'XCBGxInvert', 'XCBGxOrReverse', 'XCBGxCopyInverted', 'XCBGxOrInverted', 'XCBGxNand', 'XCBGxSet']
type XcbIcccmWmT = Literal['XCBIcccmWmHintInput', 'XCBIcccmWmHintState', 'XCBIcccmWmHintIconPixmap', 'XCBIcccmWmHintIconWindow', 'XCBIcccmWmHintIconPosition', 'XCBIcccmWmHintIconMask', 'XCBIcccmWmHintWindowGroup', 'XCBIcccmWmHintXUrgency']
type XcbImageFormatT = Literal['XCBImageFormatXyBitmap', 'XCBImageFormatXyPixmap', 'XCBImageFormatZPixmap']
type XcbImageOrderT = Literal['XCBImageOrderLsbFirst', 'XCBImageOrderMsbFirst']
type XcbInputFocusT = Literal['XCBInputFocusNone', 'XCBInputFocusPointerRoot', 'XCBInputFocusParent', 'XCBInputFocusFollowKeyboard']
type XcbLineStyleT = Literal['XCBLineStyleSolid', 'XCBLineStyleOnOffDash', 'XCBLineStyleDoubleDash']
type XcbMapStateT = Literal['XCBMapStateUnmapped', 'XCBMapStateUnviewable', 'XCBMapStateViewable']
type XcbModMaskT = Literal['XCBModMaskShift', 'XCBModMaskLock', 'XCBModMaskControl', 'XCBModMask1', 'XCBModMask2', 'XCBModMask3', 'XCBModMask4', 'XCBModMask5', 'XCBModMaskAny']
type XcbPropModeT = Literal['XCBPropModeReplace', 'XCBPropModePrepend', 'XCBPropModeAppend']
type XcbRandrNotifyMaskT = Literal['XCBRandrNotifyMaskScreenChange', 'XCBRandrNotifyMaskCrtcChange', 'XCBRandrNotifyMaskOutputChange', 'XCBRandrNotifyMaskOutputProperty', 'XCBRandrNotifyMaskProviderChange', 'XCBRandrNotifyMaskProviderProperty', 'XCBRandrNotifyMaskResourceChange']
type XcbRandrNotifyT = Literal['XCBRandrNotifyCrtcChange', 'XCBRandrNotifyOutputChange', 'XCBRandrNotifyOutputProperty', 'XCBRandrNotifyProviderChange', 'XCBRandrNotifyProviderProperty', 'XCBRandrNotifyResourceChange']
type XcbSendEventDestT = Literal['XCBSendEventDestPointerWindow', 'XCBSendEventDestItemFocus']
type XcbStackModeT = Literal['XCBStackModeAbove', 'XCBStackModeBelow', 'XCBStackModeTopIf', 'XCBStackModeBottomIf', 'XCBStackModeOpposite']
type XcbWindowClassT = Literal['XCBWindowClassCopyFromParent', 'XCBWindowClassInputOutput', 'XCBWindowClassInputOnly']
type XcbWindowEnumT = Literal['XCBWindowNone']
