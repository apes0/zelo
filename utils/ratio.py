from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.backends.generic import GDisplay, GWindow
    from ..lib.ctx import Ctx


class Ratio:
    def __init__(self, ratio: float, width: bool = False, height: bool = False) -> None:
        self.ratio = ratio
        self.width = width or not height
        self.height = height or not width

    def getRatio(self, obj: 'GDisplay | GWindow'):
        # TODO: is this a good idea?
        return (
            self.ratio
            * (obj.width * self.width + obj.height * self.height)
            / (self.width + self.height)
        )

    def default(self, ctx: 'Ctx'):
        return sum([self.getRatio(dpy) for dpy in ctx.screen.displays]) / len(
            ctx.screen.displays
        )

    def __add__(self, b: 'Ratio| int | float'):
        if isinstance(b, Ratio):
            return Ratio(self.ratio + b.ratio, width=self.width, height=self.height)
        else:
            return Ratio(self.ratio + b, width=self.width, height=self.height)

    def __sub__(self, b: 'Ratio| int | float'):
        if isinstance(b, Ratio):
            return Ratio(self.ratio - b.ratio, width=self.width, height=self.height)
        else:
            return Ratio(self.ratio - b, width=self.width, height=self.height)

    def __mul__(self, b: 'Ratio | int | float'):
        if isinstance(b, Ratio):
            return Ratio(self.ratio * b.ratio, width=self.width, height=self.height)
        else:
            return Ratio(self.ratio * b, width=self.width, height=self.height)

    def __neg__(self):
        return Ratio(-self.ratio, width=self.width, height=self.height)

    def __repr__(self) -> str:
        return f'<Ratio {self.ratio} for {["", "width", "height", "both"][self.width + self.height*2]}>'
