// types

struct wl_display;
struct wl_event_loop;

// functions

struct wl_display *wl_display_create();
const char *wl_display_add_socket_auto(struct wl_display *display);
void wl_display_run(struct wl_display *display);
void wl_display_destroy(struct wl_display *display);
int wl_event_loop_get_fd(struct wl_event_loop *loop);
void wl_display_flush_clients(struct wl_display *display);
int wl_event_loop_dispatch(struct wl_event_loop *loop, int timeout);
struct wl_event_loop *wl_display_get_event_loop(struct wl_display *display);