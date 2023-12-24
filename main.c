#include <stdio.h>
#include <pango/pango.h>
#include <pango/pangoft2.h>

int main()
{

    PangoFontMap *fontmap = pango_ft2_font_map_new();
    PangoContext *context = pango_font_map_create_context(fontmap);

    PangoLayout *layout;

    layout = pango_layout_new(context);
    PangoFontDescription *desc = pango_font_description_from_string("DejaVu Sans Bold 120");

    pango_layout_set_font_description(layout, desc);
    pango_font_description_free(desc);
    pango_layout_set_text(layout, "Hello, Pango!", -1);

    /* Render the layout to a FreeType bitmap */
    FT_Bitmap bitmap;
    pango_ft2_render_layout(&bitmap, layout, 0, 0);
}