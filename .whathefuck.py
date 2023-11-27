from cffi import FFI

ffibuilder = FFI()

ffibuilder.set_source(
    'test',
    '''
#include <xcb/xcb.h>
#include <xcb/xproto.h>
#include <xcb/xcb_util.h>
#include <sys/select.h>

void main() {
    int *screenp = 0;
    xcb_connection_t *c = xcb_connect(NULL, screenp);
    int fd = xcb_get_file_descriptor(c);
    printf("%d", fd);
    xcb_window_t root = xcb_aux_get_screen(c, screenp)->root;
    printf("%d", fd);

    xcb_grab_key(c, 1, root, XCB_MOD_MASK_ANY, XCB_GRAB_ANY, XCB_GRAB_MODE_ASYNC, XCB_GRAB_MODE_ASYNC);
    xcb_flush(c);

    fd_set read;

    FD_ZERO(&read);
    FD_SET(fd, &read);
    
    while (1)
    {
        int r = select(fd + 1, &read, NULL, NULL, NULL);
        xcb_generic_event_t *e = xcb_poll_for_event(c);
        printf("%p\\n", e);
        while (e != NULL)
        {
            e = xcb_poll_for_event(c);
            printf("more: %p\\n", e);
        }
    }
}
    ''',
    libraries=['xcb', 'xcb-util'],
)

ffibuilder.cdef(
    '''
void main();
    '''
)

ffibuilder.compile(target='*')

from test import lib

lib.main()
