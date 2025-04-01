from ..generic import GDisplay, GScreen
from .cfg import HEIGHT, ROOT, WIDTH


class Screen(GScreen):
    def __init__(self) -> None:
        self.width = WIDTH
        self.height = HEIGHT
        self.displays = [Display()]
        self.root = ROOT


class Display(GDisplay):
    def __init__(self) -> None:
        self.x = 0
        self.y = 0
        self.width = WIDTH
        self.height = HEIGHT
