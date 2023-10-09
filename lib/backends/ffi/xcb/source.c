#include <xcb/xcb.h>
#include <xcb/xproto.h>
#include <xcb/xcb_util.h>
#include <xcb/xcb_keysyms.h>
#include <xcb/xcb_image.h>

// xcb_key_symbols_t *keysyms_alloc(xcb_connection_t *c)
//{
//     printf("%d, %d - ", xcb_connection_has_error(c), !c);
//     xcb_key_symbols_t *syms = xcb_key_symbols_alloc(c);
//     return syms;
// }