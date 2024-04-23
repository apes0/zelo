from .ratio import Ratio


# TODO: maybe directly add and subtract ratios


class Layout:
    def __init__(
        self,
        x: Ratio = Ratio(0, width=True),
        y: Ratio = Ratio(0, height=True),
        width: Ratio = Ratio(1, width=True),
        height: Ratio = Ratio(1, height=True),
        spacing: float = 0,
    ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.spacing = spacing

    def hsplit(self, y: float, spacing: float):
        return Layout(
            self.x + spacing,
            self.y + spacing,
            self.width - spacing * 2,
            self.height * y - spacing * 2,
        ), Layout(
            self.x + spacing,
            self.y + self.height * y + spacing,
            self.width - spacing * 2,
            self.height * (-y + 1) - spacing * 2,
        )  # top, bottom

    def vsplit(self, x: float, spacing: float):
        return Layout(
            self.x + spacing,
            self.y + spacing,
            self.width * x - spacing * 2,
            self.height - spacing * 2,
        ), Layout(
            self.x + self.width * x + spacing,
            self.y + spacing,
            self.width * (1 - x) - spacing * 2,
            self.height - spacing * 2,
        )  # left, right

    def unspace(self):
        self.x -= self.spacing
        self.y -= self.spacing
        self.width -= 2 * self.spacing
        self.height -= 2 * self.spacing
