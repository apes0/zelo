#include <xcb/randr.h>
#include <xcb/shm.h>
#include <xcb/xcb.h>
#include <xcb/xcb_errors.h>
#include <xcb/xcb_icccm.h>
#include <xcb/xcb_image.h>
#include <xcb/xcb_keysyms.h>
#include <xcb/xcb_util.h>
#include <xcb/xinerama.h>
#include <xcb/xproto.h>
#include <xcb/xtest.h>

#include <sys/ipc.h>
#include <sys/shm.h>

// see this:
// https://stackoverflow.com/questions/27745131/how-to-use-shm-pixmap-with-xcb

typedef struct xcb_shm {
    uint32_t id;
    void *addr;
} xcb_shm;

xcb_shm create_shm(xcb_connection_t *c, size_t size) {
    xcb_shm out;

    int shmid = shmget(IPC_PRIVATE, size, IPC_CREAT | 0600);
    out.addr = shmat(shmid, 0, 0);

    out.id = xcb_generate_id(c);
    xcb_shm_attach(c, out.id, shmid, 0);
    shmctl(shmid, IPC_RMID, 0);

    return out;
}

void remove_shm(xcb_connection_t *c, xcb_shm shm) {
    xcb_shm_detach(c, shm.id);
    shmdt(shm.addr);
}

xcb_render_fixed_t double_to_fixed(double n) {
    return (xcb_render_fixed_t)(n * 65536.0);
}
