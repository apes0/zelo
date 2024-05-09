#include <xcb/xcb.h>
#include <xcb/xcb_util.h>
#include <xcb/xv.h>
#include <stdio.h>

int main() {
    int *scrp;
    xcb_connection_t *c = xcb_connect(NULL, scrp);
    xcb_window_t win = xcb_aux_get_screen(c, *scrp) -> root;
    xcb_xv_query_adaptors_reply_t *r = xcb_xv_query_adaptors_reply(c, xcb_xv_query_adaptors(c, win), NULL);
    xcb_xv_adaptor_info_iterator_t it = xcb_xv_query_adaptors_info_iterator(r);
    
    return 0;
}
