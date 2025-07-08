from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from utils.theme import Theme


class Cfg:
    def __init__(self) -> None:
        self.extensions: dict
        self.theme: Theme


# TODO: maybe add cursor stuff here when i figure it out (or move it to a plugin idk)
