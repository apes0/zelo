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

    def hsplit(self, y: float, topspacing: float = -1, bottomspacing: float = -1):
        topspacing = max(topspacing, 0)
        bottomspacing = bottomspacing if bottomspacing > 0 else topspacing

        return Layout(
            self.x + topspacing,
            self.y + topspacing,
            self.width - topspacing * 2,
            self.height * y - topspacing * 2,
        ), Layout(
            self.x + bottomspacing,
            self.y + self.height * y + bottomspacing,
            self.width - bottomspacing * 2,
            self.height * (-y + 1) - bottomspacing * 2,
        )  # top, bottom

    def vsplit(self, x: float, leftspacing: float = -1, rightspacing: float = -1):
        leftspacing = max(leftspacing, 0)
        rightspacing = rightspacing if rightspacing > 0 else leftspacing

        return Layout(
            self.x + leftspacing,
            self.y + leftspacing,
            self.width * x - leftspacing * 2,
            self.height - leftspacing * 2,
        ), Layout(
            self.x + self.width * x + rightspacing,
            self.y + rightspacing,
            self.width * (1 - x) - rightspacing * 2,
            self.height - rightspacing * 2,
        )  # left, right

    def unspace(self):
        self.x -= self.spacing
        self.y -= self.spacing
        self.width -= 2 * self.spacing
        self.height -= 2 * self.spacing
