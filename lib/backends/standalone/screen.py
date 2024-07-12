from ..generic import GScreen, GDisplay

from .cfg import ROOT, WIDTH, HEIGHT


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
