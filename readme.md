
# My window manager ~~(i need to come up with a name for it)~~

This is a window manager written in python using xcb and cffi. I made it primarily because i don't like how gnome manages windows.

# Support

- currently only a very basic window manager
- extensions
- no ewmh currently
- no icccm currently

# extensions

Currently, extensions are not ready. I will write a generic api for both x11 and wayland and only then will the extensions be usable.

There are currently these extensions:

- mouse focus - adds support for focusing on a window with the mouse
- tiler - tiles windows
- ultrawide tiler - tiles windows only horizontally
- wallpaper - does wallpapers

# Configuring

The configuration is held in ``cfg.py``, there you can put shortcuts, extensions and their config, and what to be run when the window manager starts.
