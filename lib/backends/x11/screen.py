from ..generic import GScreen


class Screen(
    GScreen
):  # idk if wayland has an equivalent for root_depth, so i wont put it here yet
    def __init__(self, screen) -> None:
        self.width: int = screen.width_in_pixels
        self.height: int = screen.height_in_pixels
        self.root: int = screen.root
        self.screen = screen
        self.num: int  # gonna use this when i eventually support multiple monitors
