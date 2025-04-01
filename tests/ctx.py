import os
from typing import TYPE_CHECKING

import trio

if TYPE_CHECKING:
    from .pres import Pre


class Ctx:
    def __init__(self, nurs: trio.Nursery) -> None:
        self.env = os.environ.copy()
        self.nurs = nurs
        self.pres: list['Pre'] = []
