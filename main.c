#include <freetype/freetype.h>
#include <pango/pango.h>
#include <pango/pangoft2.h>

int main()
{

    PangoFontMap *fontmap = pango_ft2_font_map_new();
    PangoContext *context = pango_font_map_create_context(fontmap);

    PangoLayout *layout;

    layout = pango_layout_new(context);
    PangoFontDescription *desc = pango_font_description_from_string("Ubuntu");

    pango_layout_set_font_description(layout, desc);
    pango_layout_set_text(layout, "Hi!", 3);

    FT_Bitmap bitmap;
    pango_ft2_render_layout(&bitmap, layout, 0, 0);
    for (uint i = 0; i < bitmap.rows; i++)
        for (uint j = 0; i < bitmap.width; i++)
            printf("%d", bitmap.buffer[i * bitmap.width + j]);
    pango_font_description_free(desc);
}