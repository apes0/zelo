#define HAVE_FREETYPE_FREETYPE
#include <stdio.h>
#include <stdlib.h>
#include <freetype2/freetype/ftbitmap.h>
#include <pango/pangoft2.h>
#include <pango/pango.h>

//!!! based on this:
// https://www.roxlu.com/2014/046/rendering-text-with-pango--cairo-and-freetype

int main()
{
    PangoContext *context = NULL;
    PangoLayout *layout = NULL;
    PangoFontDescription *font_desc = NULL;
    PangoFontMap *font_map = NULL;
    FT_Bitmap bmp = {0};
    FT_Library library;

    FT_Init_FreeType(&library);

    font_map = pango_ft2_font_map_new();

    context = pango_font_map_create_context(font_map);

    layout = pango_layout_new(context);

    pango_font_description_set_size(font_desc, 1000);
    font_desc = pango_font_description_from_string("Ubuntu");
    pango_layout_set_font_description(layout, font_desc);
    pango_font_map_load_font(font_map, context, font_desc);
    pango_font_description_free(font_desc);

    const char *text = "Здравей!";

    pango_layout_set_markup(layout, text, -1);

    int width;
    int height;
    pango_layout_get_size(layout, &width, &height);

    FT_Bitmap_Init(&bmp);
    bmp.rows = height / PANGO_SCALE;
    bmp.width = width / PANGO_SCALE;

    bmp.pitch = (bmp.width + 3) & -4; // align to 4 bytes?
    bmp.buffer = (unsigned char *)malloc(bmp.rows * bmp.pitch);
    bmp.pixel_mode = FT_PIXEL_MODE_GRAY; /*< Grayscale*/
    bmp.num_grays = 256;

    for (int y = 0; y < bmp.rows; y++)
        for (int x = 0; x < bmp.width; x++)
            bmp.buffer[x + y * bmp.pitch] = 0; // clear the buffer

    pango_ft2_render_layout(&bmp, layout, 0, 0);

    for (int y = 0; y < bmp.rows; y++)
    {
        for (int x = 0; x < bmp.width; x++)
        {
            unsigned char val = *(bmp.buffer + x + y * bmp.pitch);
            if (val)
                printf("%c", '#');
            else
                printf("%c", ' ');
        }
        printf("%c", '\n');
    }

    FT_Bitmap_Done(library, &bmp);
    g_object_unref(layout);
    g_object_unref(font_map);
    g_object_unref(context);

    return 0;
}
