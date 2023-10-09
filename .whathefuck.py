from cffi import FFI

ffibuilder = FFI()

ffibuilder.set_source(
    'test',
    '''
#include <xcb/xcb.h>
#include <xcb/xproto.h>
#include <xcb/xcb_util.h>
#include <xcb/xcb_keysyms.h>
#include <xcb/xcb_image.h>

void main() {
    int *screenp = 0;
    xcb_connection_t *c = xcb_connect(NULL, screenp);
    xcb_key_symbols_t *syms = xcb_key_symbols_alloc(c);
    if (!syms)
        printf("NULL");
    printf("%p", syms);
}
    ''',
    libraries=['xcb', 'xcb-util', 'xcb-image', 'xcb-keysyms'],
)

ffibuilder.cdef(
    '''
void main();
    '''
)

ffibuilder.compile(verbose=True, target='*')

from test import lib

lib.main()
