from ..generic import GScreen, GDisplay

# TODO: support xinerama as well (should not be difficult i hope)


class Display(GDisplay):
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height


class Screen(
    GScreen
):  # idk if wayland has an equivalent for root_depth, so i wont put it here yet
    def __init__(self, screen) -> None:
        self.width: int = screen.width_in_pixels
        self.height: int = screen.height_in_pixels
        self.root: int = screen.root
        self.screen = screen
        self.displays: list[Display] = []
