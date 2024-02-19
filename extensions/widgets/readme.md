# Widgets

Widgets are extensions that have a ceertain ui funciton. To use a widget, you should use the [widget](../readme.md#widget) extension. You also need to import it into the ``cfg.py`` file. Here you will find how to configure the widgets and what they do.
Anything marked with "?" is optional.

## clock

This widget shows a clock.

- ``fmt`` - the format of the clock; this uses ``time.strftime``
- ``update``? - how often the clock should update
- ``font`` - the font to use (e.g. 'Ubuntu 23')
- ``fore``? - the foreground color
- ``back``? - the background color

## hbar

This widget makes a horizontal bar.

``back``? - the background color
``height`` - the height of the bar
``width`` - the width of the bar

## nowPlaying

This widget shows what is playing right now.

- ``fmt``? - the format to use for the now playing text
- ``update``? - how often the text should update
- ``font`` - the font to use (e.g. 'Ubuntu 23')
- ``step``? - how much the text should move every update
- ``default``? - the default text for when nothing is playing
- ``width``? - the width of the text box
- ``fore``? - the foreground color
- ``back``? - the background color

> [!NOTE]
> This requires the ``dbus`` module to be installed. To install it, run ``pip3 install dbus``

## text

This widget shows a clock.

- ``text`` - the text to draw
- ``font`` - the font to use (e.g. 'Ubuntu 23')
- ``fore``? - the foreground color
- ``back``? - the background color
