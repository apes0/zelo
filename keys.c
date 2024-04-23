#include <stdio.h>
#include <stdlib.h>
#include <xcb/xcb.h>
#include <xcb/xcb_keysyms.h>

int main() {
    xcb_connection_t *conn = xcb_connect(NULL, NULL);

    xcb_get_modifier_mapping_cookie_t cookie = xcb_get_modifier_mapping_unchecked(conn);
    xcb_get_modifier_mapping_reply_t *reply = xcb_get_modifier_mapping_reply(conn, cookie, NULL);

    xcb_keycode_t *modmap = xcb_get_modifier_mapping_keycodes(reply); // first 3 are shift, lock, ctrl and then mod mask 1-5
    for (int mod_index = 0; mod_index <= 8; mod_index ++)
        for (int i = 0; i < reply->keycodes_per_modifier; i++) {
            xcb_keycode_t kc = modmap[mod_index * reply->keycodes_per_modifier + i];
            if (kc)
                printf("Keycode for modifier %d: %d\n", mod_index, kc);
        }

    free(reply);
    xcb_disconnect(conn);

    return 0;
}
