typedef struct FT_Bitmap_
{
    unsigned int rows;
    unsigned int width;
    int pitch;
    unsigned char *buffer;
    unsigned short num_grays;
    unsigned char pixel_mode;
    unsigned char palette_mode;
    void *palette;

} FT_Bitmap;

FT_Bitmap render(char *text, char *font, unsigned int back, unsigned int fore);