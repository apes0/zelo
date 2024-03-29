
# Extensions

To use an extension, you need to go to the ``cfg.py`` file and edit it's ``cfg.extensions`` dictionary. You also need to import it into said file. Here you will find how to configure the (stable) extensions and what they do.
Anything marked with "?" is optional.

# Configuring

## mouseFocus

This plugin adds the ability to focus windows when clicking on a window.
The default X11 behaviour for this is having the focus be on the window over which the mouse is.

- ``buttons``? - a list of ``Button``s which change the focus.
- ``mod`` - a modifier, required for the focus to change (idk why you would ever want this).

## shortcuts

Manages shortcuts.

- ``shortcuts``? - a dictionary with the structure of ``((Key, ...), Mod): function``.

When the keys and modifier for a shortcut are pressed, the function for them gets called.

## tiler

Tiles windows by having one main one on the left side and every other window on the right side.

- ``mainSize`` - the fraction (0 to 1) of the screen that the main window should take.
- ``border`` - the size of the border for windows.
- ``spacing`` - the spacing between windows in pixels.

## hstack

Tiles windows by having them all arranged horizontally.

- ``border`` - the size of the border for windows.
- ``spacing`` - the spacing between windows in pixels.

## vstack

Tiles windows by having them all arranged vertically.

- ``border`` - the size of the border for windows.
- ``spacing`` - the spacing between windows in pixels.

## wallpaper

Sets a wallpaper.

- ``wall`` - a path to the wallpaper.
- ``video``? - a boolean which shows if the wallpaper is a video.

## workspaces

Adds support for workspaces.

- ``next`` - The shortcut (refer to [shortcuts](#shortcuts)) for switching to the next workspace
- ``prev`` - The shortcut for switching to the previous workspace
- ``move`` -The shortcut for marking a window to move to a different workspace

## widget

Puts [widgets](./widgets/readme.md) on your desktop.

- ``widgets`` - a dictionary of all the widgets to display and their configs with the structure of ``Widget: dict``

## mouse

Makes the mouse be rendered in a certain color and font.

- ``font``? - the font to use for the cursor
- ``cursor``? - the name of the cursor icon
- ``fore``? - the foreground color
- ``back``? - the background color
