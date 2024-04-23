class Theme:
    def __init__(self, fore: int, back: int, colors: list[int]) -> None:
        self.fore = fore
        self.back = back
        self.colors = colors

    def getColor(self, col, size):
        # get a color of some number with a pallet of an imaginary size
        actual = len(self.colors)
        ratio = actual / size
        return self.colors[round(col * ratio)]
