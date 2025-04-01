import pywal

from .theme import Theme


def getColor(col: str):
    if col.startswith('#'):
        col = col[1:]

    return int(col, base=16)


def getTheme(wall: str):
    colors = pywal.colors.get(wall)
    assert colors, 'pywal failed to generate a pallet...'
    return Theme(
        fore=getColor(colors['special']['foreground']),
        back=getColor(colors['special']['background']),
        colors=[getColor(col) for col in colors['colors'].values()],
    )
