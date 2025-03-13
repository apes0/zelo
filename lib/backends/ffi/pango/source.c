#define HAVE_FREETYPE_FREETYPE
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <freetype2/freetype/ftbitmap.h>
#include <pango/pangoft2.h>
#include <pango/pango.h>

// !!! based on this:
// https://www.roxlu.com/2014/046/rendering-text-with-pango--cairo-and-freetype

FT_Bitmap render(char *text, char *font, int back, int fore)
{
    FT_Bitmap bmp = {0};
    PangoContext *context = NULL;
    PangoLayout *layout = NULL;
    PangoFontDescription *font_desc = NULL;
    PangoFontMap *font_map = NULL;

    font_map = pango_ft2_font_map_new();

    context = pango_font_map_create_context(font_map);

    layout = pango_layout_new(context);

    font_desc = pango_font_description_from_string(font);
    pango_layout_set_font_description(layout, font_desc);
    pango_font_map_load_font(font_map, context, font_desc);
    pango_font_description_free(font_desc);

    pango_layout_set_markup(layout, text, -1);

    int width;
    int height;
    pango_layout_get_size(layout, &width, &height);

    FT_Bitmap_Init(&bmp);
    bmp.rows = height / PANGO_SCALE;
    bmp.width = width / PANGO_SCALE;

    bmp.pitch = (bmp.width + 3) & -4; // idfk man
    bmp.buffer = (unsigned char *)malloc(bmp.rows * bmp.pitch);
    bmp.pixel_mode = FT_PIXEL_MODE_GRAY; /*< Grayscale*/
    bmp.num_grays = 256;

    for (uint y = 0; y < bmp.rows; y++)
        for (uint x = 0; x < bmp.width; x++)
            bmp.buffer[x + y * bmp.pitch] = 0; // clear the buffer

    pango_ft2_render_layout(&bmp, layout, 0, 0);

    unsigned char *out = (unsigned char *)malloc(bmp.rows * bmp.width * 4);

    // fml
    float fr = (float)((back) & 255) / 255;
    float fg = (float)((back >> 8) & 255) / 255;
    float fb = (float)((back >> 16) & 255) / 255;
    float br = (float)((fore) & 255) / 255;
    float bg = (float)((fore >> 8) & 255) / 255;
    float bb = (float)((fore >> 16) & 255) / 255;

    for (uint y = 0; y < bmp.rows; y++)
        for (uint x = 0; x < bmp.width; x++)
        {
            unsigned char col = bmp.buffer[x + y * bmp.pitch];
            out[(x + y * bmp.width) * 4 + 0] = (255 - col) * br + col * fr;
            out[(x + y * bmp.width) * 4 + 1] = (255 - col) * bg + col * fg;
            out[(x + y * bmp.width) * 4 + 2] = (255 - col) * bb + col * fb;
            out[(x + y * bmp.width) * 4 + 3] = 255;
        }

    free(bmp.buffer);
    bmp.buffer = out;

    //    FT_Bitmap_Done(library, &bmp);
    g_object_unref(layout);
    g_object_unref(font_map);
    g_object_unref(context);

    return bmp;
}
