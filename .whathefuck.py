from cffi import FFI

ffibuilder = FFI()

ffibuilder.set_source(
    'test',
    '''
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
    pango_layout_set_text(layout, "Fuck you, Pango!", -1);

    FT_Bitmap bitmap;
    pango_ft2_render_layout(&bitmap, layout, 0, 0);
    
    return 0;
}
    ''',
    libraries=['pango', 'pangoft2', 'fontconfig', 'freetype'],
)

ffibuilder.cdef(
    '''
void main();
    '''
)

ffibuilder.compile(target='*')

from test import lib

lib.main()
