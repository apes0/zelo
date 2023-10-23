
# Zelo

This is a window manager written in python. I made it primarily because i don't like how gnome manages windows.

# Support

- only x11, but i am going to work on wayland support
- extensions
- no ewmh currently
- no icccm currently

# extensions

Currently, extensions are not ready. I am writing a generic api for both x11 and wayland and only then will the extensions be usable.

That being said, these are the currently available extensions:

- mouse focus - adds support for focusing on a window with the mouse
- tiler - tiles windows (i think the tiling method is called 'zoomy')
- ultrawide tiler - tiles windows only vertically
- wallpaper - sets a wallpaper
- shortcuts - manages shortcuts
- workspaces - adds support for workspaces
- fake monitors - adds support for making multiple fake monitors on one monitor

# Installation

## Debian or Ubuntu

There is currently an install script, located in ``scripts/setup.sh``, but it works only on Debian
and Ubuntu (i have tested it on both).

## Anything else

If you are running anything unsupported by the install script, you need to do the following:

- dowload the following dependencies: ``libxcb-util-dev libx11-xcb-dev libxcb-keysyms1-dev libxcb-image0-dev libxcb-randr0-dev python3``

- run ``pip3 install -r requirements.py`` or install the following modules from your package manager: ``python3-cffi python3-opencv``

- finally, run ``./scripts/keysyms.sh``

# Configuring

The configuration is held in ``cfg.py``, there you can put shortcuts, extensions and their config, and what to be run when the window manager starts. I might add more info about how to configure the window manager.

# Docs

Realistically, i am going to be the only person who will actually use this, and i am also probably never going to finish the docs, but if i do finish them, there will be a link to them here.

# Images

![dirty](.assets/dirty.png)
