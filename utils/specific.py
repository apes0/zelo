from lib.backends.generic import GDisplay


class On:
    def __init__(self, dpy: 'GDisplay', mine: dict, others: dict) -> None:
        self.dpy = dpy
        self.mine = mine
        self.others = others
