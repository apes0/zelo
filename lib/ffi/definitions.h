/*
i found most of these with these commands:
``
lookfor=('xcb_change_window_attributes_checked' 'xcb_ungrab_key' ...)
cpped=`cpp <(echo "#include <xcb/xcb.h>\n#include<xcb/xcb_util.h>\n#include <xcb/xcb_keysyms.h>")`
for look in $lookfor
do
echo $look
echo $cpped | egrep -zo $(echo '[^;]*\\n[^;]*'$look'[^;]*;')
echo
done
``
or by exploring via this if there was no result(or it wasn't helpful):
echo $cpped | grep -n <something>
or
echo $cpped | less
*/

// types

typedef struct xcb_connection_t xcb_connection_t;
typedef unsigned int xcb_window_t;
typedef unsigned int xcb_visualid_t;
typedef unsigned int xcb_colormap_t;
typedef struct
{
    xcb_window_t root;
    xcb_colormap_t default_colormap;
    unsigned int white_pixel;
    unsigned int black_pixel;
    unsigned int current_input_masks;
    unsigned short width_in_pixels;
    unsigned short height_in_pixels;
    unsigned short width_in_millimeters;
    unsigned short height_in_millimeters;
    unsigned short min_installed_maps;
    unsigned short max_installed_maps;
    xcb_visualid_t root_visual;
    unsigned char backing_stores;
    unsigned char save_unders;
    unsigned char root_depth;
    unsigned char allowed_depths_len;
} xcb_screen_t;
typedef struct
{
    unsigned int sequence;
} xcb_void_cookie_t;
typedef unsigned int xcb_cursor_t;
typedef unsigned char xcb_keycode_t;
typedef struct
{
    unsigned char response_type;
    unsigned char pad0;
    unsigned short sequence;
    unsigned int pad[7];
    unsigned int full_sequence;
} xcb_generic_event_t;
typedef unsigned char xcb_button_t;
typedef unsigned int xcb_timestamp_t;
typedef struct xcb_button_press_event_t
{
    unsigned char response_type;
    xcb_button_t detail;
    unsigned short sequence;
    xcb_timestamp_t time;
    xcb_window_t root;
    xcb_window_t event;
    xcb_window_t child;
    short root_x;
    short root_y;
    short event_x;
    short event_y;
    unsigned short state;
    unsigned char same_screen;
    unsigned char pad0;
} xcb_button_press_event_t;
typedef enum xcb_config_window_t
{
    XCB_CONFIG_WINDOW_X = 1,
    XCB_CONFIG_WINDOW_Y = 2,
    XCB_CONFIG_WINDOW_WIDTH = 4,
    XCB_CONFIG_WINDOW_HEIGHT = 8,
    XCB_CONFIG_WINDOW_BORDER_WIDTH = 16,
    XCB_CONFIG_WINDOW_SIBLING = 32,
    XCB_CONFIG_WINDOW_STACK_MODE = 64
} xcb_config_window_t;
typedef enum xcb_input_focus_t
{
    XCB_INPUT_FOCUS_NONE = 0,
    XCB_INPUT_FOCUS_POINTER_ROOT = 1,
    XCB_INPUT_FOCUS_PARENT = 2,
    XCB_INPUT_FOCUS_FOLLOW_KEYBOARD = 3
} xcb_input_focus_t;
typedef enum xcb_cw_t
{
    XCB_CW_BACK_PIXMAP = 1,
    XCB_CW_BACK_PIXEL = 2,
    XCB_CW_BORDER_PIXMAP = 4,
    XCB_CW_BORDER_PIXEL = 8,
    XCB_CW_BIT_GRAVITY = 16,
    XCB_CW_WIN_GRAVITY = 32,
    XCB_CW_BACKING_STORE = 64,
    XCB_CW_BACKING_PLANES = 128,
    XCB_CW_BACKING_PIXEL = 256,
    XCB_CW_OVERRIDE_REDIRECT = 512,
    XCB_CW_SAVE_UNDER = 1024,
    XCB_CW_EVENT_MASK = 2048,
    XCB_CW_DONT_PROPAGATE = 4096,
    XCB_CW_COLORMAP = 8192,
    XCB_CW_CURSOR = 16384
} xcb_cw_t;
typedef struct xcb_key_press_event_t
{
    unsigned char response_type;
    xcb_keycode_t detail;
    unsigned short sequence;
    xcb_timestamp_t time;
    xcb_window_t root;
    xcb_window_t event;
    xcb_window_t child;
    short root_x;
    short root_y;
    short event_x;
    short event_y;
    unsigned short state;
    unsigned char same_screen;
    unsigned char pad0;
} xcb_key_press_event_t;

typedef struct xcb_motion_notify_event_t
{
    unsigned char response_type;
    unsigned char detail;
    unsigned short sequence;
    xcb_timestamp_t time;
    xcb_window_t root;
    xcb_window_t event;
    xcb_window_t child;
    short root_x;
    short root_y;
    short event_x;
    short event_y;
    unsigned short state;
    unsigned char same_screen;
    unsigned char pad0;
} xcb_motion_notify_event_t;
typedef struct xcb_create_notify_event_t
{
    unsigned char response_type;
    unsigned char pad0;
    unsigned short sequence;
    xcb_window_t parent;
    xcb_window_t window;
    short x;
    short y;
    unsigned short width;
    unsigned short height;
    unsigned short border_width;
    unsigned char override_redirect;
    unsigned char pad1;
} xcb_create_notify_event_t;
typedef struct xcb_map_request_event_t
{
    unsigned char response_type;
    unsigned char pad0;
    unsigned short sequence;
    xcb_window_t parent;
    xcb_window_t window;
} xcb_map_request_event_t;
typedef enum xcb_mod_mask_t
{
    XCB_MOD_MASK_SHIFT = 1,
    XCB_MOD_MASK_LOCK = 2,
    XCB_MOD_MASK_CONTROL = 4,
    XCB_MOD_MASK_1 = 8,
    XCB_MOD_MASK_2 = 16,
    XCB_MOD_MASK_3 = 32,
    XCB_MOD_MASK_4 = 64,
    XCB_MOD_MASK_5 = 128,
    XCB_MOD_MASK_ANY = 32768
} xcb_mod_mask_t;
typedef struct xcb_configure_request_event_t
{
    unsigned char response_type;
    unsigned char stack_mode;
    unsigned short sequence;
    xcb_window_t parent;
    xcb_window_t window;
    xcb_window_t sibling;
    short x;
    short y;
    unsigned short width;
    unsigned short height;
    unsigned short border_width;
    unsigned short value_mask;
} xcb_configure_request_event_t;
typedef struct xcb_configure_notify_event_t
{
    unsigned char response_type;
    unsigned char pad0;
    unsigned short sequence;
    xcb_window_t event;
    xcb_window_t window;
    xcb_window_t above_sibling;
    short x;
    short y;
    unsigned short width;
    unsigned short height;
    unsigned short border_width;
    unsigned char override_redirect;
    unsigned char pad1;
} xcb_configure_notify_event_t;
typedef struct xcb_enter_notify_event_t
{
    unsigned char response_type;
    unsigned char detail;
    unsigned short sequence;
    xcb_timestamp_t time;
    xcb_window_t root;
    xcb_window_t event;
    xcb_window_t child;
    short root_x;
    short root_y;
    short event_x;
    short event_y;
    unsigned short state;
    unsigned char mode;
    unsigned char same_screen_focus;
} xcb_enter_notify_event_t;
typedef enum xcb_window_enum_t
{
    XCB_WINDOW_NONE = 0
} xcb_window_enum_t;
typedef enum xcb_prop_mode_t
{
    XCB_PROP_MODE_REPLACE = 0,
    XCB_PROP_MODE_PREPEND = 1,
    XCB_PROP_MODE_APPEND = 2
} xcb_prop_mode_t;
typedef struct xcb_focus_in_event_t
{
    unsigned char response_type;
    unsigned char detail;
    unsigned short sequence;
    xcb_window_t event;
    unsigned char mode;
    unsigned char pad0[3];
} xcb_focus_in_event_t;
typedef unsigned int xcb_atom_t;
typedef union xcb_client_message_data_t
{
    unsigned char data8[20];
    unsigned short data16[10];
    unsigned int data32[5];
} xcb_client_message_data_t;
typedef struct xcb_client_message_event_t
{
    unsigned char response_type;
    unsigned char format;
    unsigned short sequence;
    xcb_window_t window;
    xcb_atom_t type;
    xcb_client_message_data_t data;
} xcb_client_message_event_t;
typedef struct xcb_destroy_notify_event_t
{
    unsigned char response_type;
    unsigned char pad0;
    unsigned short sequence;
    xcb_window_t event;
    xcb_window_t window;
} xcb_destroy_notify_event_t;
typedef struct xcb_get_atom_name_reply_t
{
    unsigned char response_type;
    unsigned char pad0;
    unsigned short sequence;
    unsigned int length;
    unsigned short name_len;
    unsigned char pad1[22];
} xcb_get_atom_name_reply_t;
typedef struct xcb_get_atom_name_cookie_t
{
    unsigned int sequence;
} xcb_get_atom_name_cookie_t;
typedef struct xcb_intern_atom_reply_t
{
    unsigned char response_type;
    unsigned char pad0;
    unsigned short sequence;
    unsigned int length;
    xcb_atom_t atom;
} xcb_intern_atom_reply_t;
typedef struct xcb_intern_atom_cookie_t
{
    unsigned int sequence;
} xcb_intern_atom_cookie_t;
typedef struct
{
    unsigned char response_type;
    unsigned char error_code;
    unsigned short sequence;
    unsigned int resource_id;
    unsigned short minor_code;
    unsigned char major_code;
    unsigned char pad0;
    unsigned int pad[5];
    unsigned int full_sequence;
} xcb_generic_error_t;
typedef struct xcb_get_atom_name_request_t
{
    unsigned char major_opcode;
    unsigned char pad0;
    unsigned short length;
    xcb_atom_t atom;
} xcb_get_atom_name_request_t;
typedef enum xcb_atom_enum_t
{
    XCB_ATOM_NONE = 0,
    XCB_ATOM_ANY = 0,
    XCB_ATOM_PRIMARY = 1,
    XCB_ATOM_SECONDARY = 2,
    XCB_ATOM_ARC = 3,
    XCB_ATOM_ATOM = 4,
    XCB_ATOM_BITMAP = 5,
    XCB_ATOM_CARDINAL = 6,
    XCB_ATOM_COLORMAP = 7,
    XCB_ATOM_CURSOR = 8,
    XCB_ATOM_CUT_BUFFER0 = 9,
    XCB_ATOM_CUT_BUFFER1 = 10,
    XCB_ATOM_CUT_BUFFER2 = 11,
    XCB_ATOM_CUT_BUFFER3 = 12,
    XCB_ATOM_CUT_BUFFER4 = 13,
    XCB_ATOM_CUT_BUFFER5 = 14,
    XCB_ATOM_CUT_BUFFER6 = 15,
    XCB_ATOM_CUT_BUFFER7 = 16,
    XCB_ATOM_DRAWABLE = 17,
    XCB_ATOM_FONT = 18,
    XCB_ATOM_INTEGER = 19,
    XCB_ATOM_PIXMAP = 20,
    XCB_ATOM_POINT = 21,
    XCB_ATOM_RECTANGLE = 22,
    XCB_ATOM_RESOURCE_MANAGER = 23,
    XCB_ATOM_RGB_COLOR_MAP = 24,
    XCB_ATOM_RGB_BEST_MAP = 25,
    XCB_ATOM_RGB_BLUE_MAP = 26,
    XCB_ATOM_RGB_DEFAULT_MAP = 27,
    XCB_ATOM_RGB_GRAY_MAP = 28,
    XCB_ATOM_RGB_GREEN_MAP = 29,
    XCB_ATOM_RGB_RED_MAP = 30,
    XCB_ATOM_STRING = 31,
    XCB_ATOM_VISUALID = 32,
    XCB_ATOM_WINDOW = 33,
    XCB_ATOM_WM_COMMAND = 34,
    XCB_ATOM_WM_HINTS = 35,
    XCB_ATOM_WM_CLIENT_MACHINE = 36,
    XCB_ATOM_WM_ICON_NAME = 37,
    XCB_ATOM_WM_ICON_SIZE = 38,
    XCB_ATOM_WM_NAME = 39,
    XCB_ATOM_WM_NORMAL_HINTS = 40,
    XCB_ATOM_WM_SIZE_HINTS = 41,
    XCB_ATOM_WM_ZOOM_HINTS = 42,
    XCB_ATOM_MIN_SPACE = 43,
    XCB_ATOM_NORM_SPACE = 44,
    XCB_ATOM_MAX_SPACE = 45,
    XCB_ATOM_END_SPACE = 46,
    XCB_ATOM_SUPERSCRIPT_X = 47,
    XCB_ATOM_SUPERSCRIPT_Y = 48,
    XCB_ATOM_SUBSCRIPT_X = 49,
    XCB_ATOM_SUBSCRIPT_Y = 50,
    XCB_ATOM_UNDERLINE_POSITION = 51,
    XCB_ATOM_UNDERLINE_THICKNESS = 52,
    XCB_ATOM_STRIKEOUT_ASCENT = 53,
    XCB_ATOM_STRIKEOUT_DESCENT = 54,
    XCB_ATOM_ITALIC_ANGLE = 55,
    XCB_ATOM_X_HEIGHT = 56,
    XCB_ATOM_QUAD_WIDTH = 57,
    XCB_ATOM_WEIGHT = 58,
    XCB_ATOM_POINT_SIZE = 59,
    XCB_ATOM_RESOLUTION = 60,
    XCB_ATOM_COPYRIGHT = 61,
    XCB_ATOM_NOTICE = 62,
    XCB_ATOM_FONT_NAME = 63,
    XCB_ATOM_FAMILY_NAME = 64,
    XCB_ATOM_FULL_NAME = 65,
    XCB_ATOM_CAP_HEIGHT = 66,
    XCB_ATOM_WM_CLASS = 67,
    XCB_ATOM_WM_TRANSIENT_FOR = 68
} xcb_atom_enum_t;
typedef struct xcb_unmap_notify_event_t
{
    unsigned char response_type;
    unsigned char pad0;
    unsigned short sequence;
    xcb_window_t event;
    xcb_window_t window;
    unsigned char from_configure;
    unsigned char pad1[3];
} xcb_unmap_notify_event_t;
typedef struct xcb_map_notify_event_t
{
    unsigned char response_type;
    unsigned char pad0;
    unsigned short sequence;
    xcb_window_t event;
    xcb_window_t window;
    unsigned char override_redirect;
    unsigned char pad1[3];
} xcb_map_notify_event_t;
typedef enum xcb_send_event_dest_t
{
    XCB_SEND_EVENT_DEST_POINTER_WINDOW = 0,
    XCB_SEND_EVENT_DEST_ITEM_FOCUS = 1
} xcb_send_event_dest_t;
typedef struct xcb_get_property_cookie_t
{
    unsigned int sequence;
} xcb_get_property_cookie_t;
typedef struct xcb_get_property_reply_t
{
    unsigned char response_type;
    unsigned char format;
    unsigned short sequence;
    unsigned int length;
    xcb_atom_t type;
    unsigned int bytes_after;
    unsigned int value_len;
    unsigned char pad0[12];
} xcb_get_property_reply_t;
typedef enum xcb_get_property_type_t {
    XCB_GET_PROPERTY_TYPE_ANY = 0
} xcb_get_property_type_t;
typedef enum xcb_event_mask_t {
    XCB_EVENT_MASK_NO_EVENT = 0,
    XCB_EVENT_MASK_KEY_PRESS = 1,
    XCB_EVENT_MASK_KEY_RELEASE = 2,
    XCB_EVENT_MASK_BUTTON_PRESS = 4,
    XCB_EVENT_MASK_BUTTON_RELEASE = 8,
    XCB_EVENT_MASK_ENTER_WINDOW = 16,
    XCB_EVENT_MASK_LEAVE_WINDOW = 32,
    XCB_EVENT_MASK_POINTER_MOTION = 64,
    XCB_EVENT_MASK_POINTER_MOTION_HINT = 128,
    XCB_EVENT_MASK_BUTTON_1_MOTION = 256,
    XCB_EVENT_MASK_BUTTON_2_MOTION = 512,
    XCB_EVENT_MASK_BUTTON_3_MOTION = 1024,
    XCB_EVENT_MASK_BUTTON_4_MOTION = 2048,
    XCB_EVENT_MASK_BUTTON_5_MOTION = 4096,
    XCB_EVENT_MASK_BUTTON_MOTION = 8192,
    XCB_EVENT_MASK_KEYMAP_STATE = 16384,
    XCB_EVENT_MASK_EXPOSURE = 32768,
    XCB_EVENT_MASK_VISIBILITY_CHANGE = 65536,
    XCB_EVENT_MASK_STRUCTURE_NOTIFY = 131072,
    XCB_EVENT_MASK_RESIZE_REDIRECT = 262144,
    XCB_EVENT_MASK_SUBSTRUCTURE_NOTIFY = 524288,
    XCB_EVENT_MASK_SUBSTRUCTURE_REDIRECT = 1048576,
    XCB_EVENT_MASK_FOCUS_CHANGE = 2097152,
    XCB_EVENT_MASK_PROPERTY_CHANGE = 4194304,
    XCB_EVENT_MASK_COLOR_MAP_CHANGE = 8388608,
    XCB_EVENT_MASK_OWNER_GRAB_BUTTON = 16777216
} xcb_event_mask_t;
typedef enum xcb_button_index_t {
    XCB_BUTTON_INDEX_ANY = 0,
    XCB_BUTTON_INDEX_1 = 1,
    XCB_BUTTON_INDEX_2 = 2,
    XCB_BUTTON_INDEX_3 = 3,
    XCB_BUTTON_INDEX_4 = 4,
    XCB_BUTTON_INDEX_5 = 5
} xcb_button_index_t;

// functions

xcb_connection_t *xcb_connect(const char *displayname, int *screenp);
int xcb_connection_has_error(xcb_connection_t *c);
void xcb_disconnect(xcb_connection_t *c);
unsigned int xcb_generate_id(xcb_connection_t *c);
xcb_screen_t *xcb_aux_get_screen(xcb_connection_t *c, int screen);
xcb_void_cookie_t xcb_grab_button(xcb_connection_t *c, unsigned char owner_events, xcb_window_t grab_window, unsigned short event_mask, unsigned char pointer_mode, unsigned char keyboard_mode, xcb_window_t confine_to, xcb_cursor_t cursor, unsigned char button, unsigned short modifiers);
xcb_void_cookie_t xcb_change_window_attributes_checked(xcb_connection_t *c, xcb_window_t window, unsigned int value_mask, const void *value_list);
xcb_void_cookie_t xcb_ungrab_key(xcb_connection_t *c, xcb_keycode_t key, xcb_window_t grab_window, unsigned short modifiers);
xcb_void_cookie_t xcb_grab_key(xcb_connection_t *c, unsigned char owner_events, xcb_window_t grab_window, unsigned short modifiers, xcb_keycode_t key, unsigned char pointer_mode, unsigned char keyboard_mode);
int xcb_flush(xcb_connection_t *c);
xcb_void_cookie_t xcb_grab_button(xcb_connection_t *c, unsigned char owner_events, xcb_window_t grab_window, unsigned short event_mask, unsigned char pointer_mode, unsigned char keyboard_mode, xcb_window_t confine_to, xcb_cursor_t cursor, unsigned char button, unsigned short modifiers);
xcb_generic_event_t *xcb_wait_for_event(xcb_connection_t *c);
xcb_void_cookie_t xcb_map_window(xcb_connection_t *c, xcb_window_t window);
xcb_void_cookie_t xcb_configure_window(xcb_connection_t *c, xcb_window_t window, unsigned short value_mask, const void *value_list);
xcb_void_cookie_t xcb_set_input_focus(xcb_connection_t *c, unsigned char revert_to, xcb_window_t focus, xcb_timestamp_t time);
xcb_void_cookie_t xcb_change_property(xcb_connection_t *conn, unsigned char mode, xcb_window_t window, xcb_atom_t property, xcb_atom_t type, unsigned char format, unsigned int data_len, const void *data);
xcb_void_cookie_t xcb_delete_property(xcb_connection_t *conn, xcb_window_t window, xcb_atom_t property);
xcb_get_atom_name_cookie_t xcb_get_atom_name(xcb_connection_t *conn, xcb_atom_t atom);
xcb_intern_atom_cookie_t xcb_intern_atom(xcb_connection_t *conn, unsigned char only_if_exists, unsigned short name_len, const char *name);
xcb_get_atom_name_reply_t *xcb_get_atom_name_reply(xcb_connection_t *conn, xcb_get_atom_name_cookie_t cookie, xcb_generic_error_t **e);
xcb_intern_atom_reply_t *xcb_intern_atom_reply(xcb_connection_t *conn, xcb_intern_atom_cookie_t cookie, xcb_generic_error_t **e);
char *xcb_get_atom_name_name(const xcb_get_atom_name_reply_t *R);
xcb_void_cookie_t xcb_send_event(xcb_connection_t *conn, bool propagate, xcb_window_t destination, unsigned int event_mask, const char *event);
xcb_get_property_cookie_t xcb_get_property(xcb_connection_t *conn, unsigned char _delete, xcb_window_t window, xcb_atom_t property, xcb_atom_t type, unsigned int long_offset, unsigned int long_length);
xcb_get_property_reply_t *xcb_get_property_reply(xcb_connection_t *conn, xcb_get_property_cookie_t cookie, xcb_generic_error_t **e);
void *xcb_get_property_value(const xcb_get_property_reply_t *reply);
xcb_void_cookie_t xcb_ungrab_button(xcb_connection_t *conn, unsigned char button, xcb_window_t grab_window, unsigned short modifiers);

// weird values

unsigned int XCB_GRAB_ANY = 0;
unsigned int XCB_GRAB_MODE_ASYNC = 1;
unsigned int XCB_NONE = 0;
unsigned int XCB_GRAB_ANY = 0; // just for testing the keyboard :)
#define XCB_CURRENT_TIME 0L
// these events will never appear in cpp, so i just took the definitions from the docs
#define XCB_KEY_PRESS 2
#define XCB_KEY_RELEASE 3
#define XCB_BUTTON_PRESS 4
#define XCB_BUTTON_RELEASE 5
#define XCB_MOTION_NOTIFY 6
#define XCB_ENTER_NOTIFY 7
#define XCB_LEAVE_NOTIFY 8
#define XCB_FOCUS_IN 9
#define XCB_FOCUS_OUT 10
#define XCB_KEYMAP_NOTIFY 11
#define XCB_EXPOSE 12
#define XCB_GRAPHICS_EXPOSURE 13
#define XCB_NO_EXPOSURE 14
#define XCB_VISIBILITY_NOTIFY 15
#define XCB_CREATE_NOTIFY 16
#define XCB_DESTROY_NOTIFY 17
#define XCB_UNMAP_NOTIFY 18
#define XCB_MAP_NOTIFY 19
#define XCB_MAP_REQUEST 20
#define XCB_REPARENT_NOTIFY 21
#define XCB_CONFIGURE_NOTIFY 22
#define XCB_CONFIGURE_REQUEST 23
#define XCB_GRAVITY_NOTIFY 24
#define XCB_RESIZE_REQUEST 25
#define XCB_CIRCULATE_NOTIFY 26
#define XCB_CIRCULATE_REQUEST 27
#define XCB_PROPERTY_NOTIFY 28
#define XCB_SELECTION_CLEAR 29
#define XCB_SELECTION_REQUEST 30
#define XCB_SELECTION_NOTIFY 31
#define XCB_COLORMAP_NOTIFY 32
#define XCB_CLIENT_MESSAGE 33
#define XCB_MAPPING_NOTIFY 34
#define XCB_GE_GENERIC 35