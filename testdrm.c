#include <drm_fourcc.h>
#include <stdio.h>
#include <fcntl.h>
#include <xf86drm.h>
#include <xf86drmMode.h>
#include <sys/mman.h>
#include <string.h>
#include <stdint.h>

// you need to install libdrm-dev
//helpful: https://github.com/ascent12/drm_doc/blob/master/02_modesetting/02_modesetting.md

uint32_t getCrtc(int32_t fd, drmModeConnector* conn, drmModeRes* res, uint32_t* taken) {
    for (uint32_t i = 0; i < conn->count_encoders; i++) { // list all encoders
        drmModeEncoder *enc = drmModeGetEncoder(fd, conn->encoders[i]);

        if (!enc)
            continue;
        
        for (uint32_t j = 0; j < res->count_crtcs; j++) { // do checks for each crtc
            uint32_t bit = 1 << j;
            
            if (!(enc->possible_crtcs & bit) | *taken & bit) // are they compatible and free
                continue;


            drmModeFreeEncoder(enc);
            *taken |= bit;
            return res->crtcs[j];
        }
        drmModeFreeEncoder(enc);
    }

    return 0; // nothing was found :/
}

void makeFb(int32_t fd, uint32_t crtc, drmModeConnector *conn) {
    int32_t ret;
    for (int i = 0; i < conn->count_modes; i++)
        printf("mode %d: %dx%d @ %d\n", i, conn->modes[i].vdisplay, conn->modes[i].hdisplay, conn->modes[i].vrefresh);
    drmModeModeInfoPtr modes = conn->modes;
    drmModeModeInfo mode = modes[0];

    struct drm_mode_create_dumb create = {
        .width = mode.vdisplay,
        .height = mode.hdisplay,
        .bpp = 32, // todo: how to get this?
    };

    ret = drmIoctl(fd, DRM_IOCTL_MODE_CREATE_DUMB, &create);
    if (ret < 0)
        return;

    uint32_t handles[4] = {create.handle};
    uint32_t pitches[4] = {create.pitch};
    uint32_t offsets[4] = {0};

    uint32_t fb = 0;
    ret = drmModeAddFB2(fd, create.width, create.height, DRM_FORMAT_XRGB8888, handles, pitches, offsets, &fb, 0);
    if (ret < 0)
        return;
    
    struct drm_mode_map_dumb map = { .handle = create.handle };
    ret = drmIoctl(fd, DRM_IOCTL_MODE_MAP_DUMB, &map);

    uint8_t *data = mmap(0, create.size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, map.offset);
    if ((data == MAP_FAILED) | (ret < 0))
        return;

    memset(data, 0xff, create.size);

    ret = drmModeSetCrtc(fd, crtc, fb, 0, 0, &(conn->connector_id), 1, &mode);
    printf("ret: %d", ret);
    if (ret < 0)
        return;

    for (uint32_t y = 0; y < mode.hdisplay; y++) {
        uint8_t *row = data + create.pitch * y;

        for (uint32_t x = 0; x < mode.vdisplay; ++x) {
            row[x * 4 + 0] = 255;
            row[x * 4 + 1] = 255;
            row[x * 4 + 2] = 255;
            row[x * 4 + 3] = 255;
        }
    }
}

int main() {
    int32_t fd = open("/dev/dri/card0", O_RDWR | O_NONBLOCK); // TODO: read the env variable for this lol
    uint32_t taken = 0;

    drmModeRes *res = drmModeGetResources(fd);

    for (int32_t i = 0; i < res->count_connectors; i++) { // list all connectors
        drmModeConnector *conn = drmModeGetConnector(fd, res->connectors[i]);
        if (!conn | conn->connection != DRM_MODE_CONNECTED | !conn->count_modes) // if conn doesnt exist or isnt connected or it has no modes
            continue;

        uint32_t crtc = getCrtc(fd, conn, res, &taken);
        if (!crtc)
            continue; // we didnt find a crtc

        makeFb(fd, crtc, conn);

        drmModeFreeConnector(conn);
    }
    drmModeFreeResources(res);
}
