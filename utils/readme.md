
# Utilities

This is a collection of (simple) utilities. These are different from extensions because they do not add any new features. Instead, they are mostly useful for easier configuration.
Anything marked with "?" is optional.

# Usage

To use any of these, you should import it into your config file.

## theme.Theme

This is a class representing a theme.

- ``fore`` - the foreground color
- ``back`` - the background color
- ``colors`` - the other colors

## ratio.Ratio

This represents a ratio of a screen's size. This is useful if you have multiple screens with different sizes, but want everything to look the same.

- ``ratio`` - the ratio
- ``width``? - if the ratio is only width-wise
- ``height``? - if the ratio is only height-wise

## layout.Layout

This class represents a layout. It is basically a map of the screen that you split to get smaller areas that you can asign to certain components (e.g. widgets or the tiler).

This class has the following methods:

- ``hsplit(y: float, spacing: float)`` - splits horizontally at y% of the layout
- ``vsplit(x: float, spacing: float)`` - splits vertically at x% of the layout
- ``unspace()`` - Removes the applied spacing

## log.log

This function enables logging to a file using python's ``logging`` module. This is more of a debugging utility than anything else.

- ``file`` - the file in which the log should be written
- ``level``? - the log level (``logging.DEBUG`` by default)

## log.logTerm

This function enables logging to the console using python's ``logging`` module.

- ``level``? - the log level (``logging.DEBUG`` by default)

## pywal.getTheme

This function returns a [``Theme``](#themetheme) object generated by pywal.

- ``wall`` - the wallpaper to generate a theme for

## fns.spawn

This is a function to spawn a process.

- ``proc`` - the process to spawn

## fns.stop

This is a function to stop the window manager.

- ``ctx`` - the context (the ``Ctx`` object)
