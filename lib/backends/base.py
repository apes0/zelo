from _cffi_backend import _CDataBase


def parseArgs(args):
    out = []

    for arg in args:
        if isinstance(arg, Base):
            out.append(arg.obj)
            continue

        out.append(arg)

    return out


class Base:
    def __init__(self) -> None:
        self.obj: _CDataBase

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, _CDataBase):
            return self.obj == __value
        return self.__dict__ == __value.__dict__

    def __getitem__(self, itm):
        return self.obj[itm]

    def __repr__(self) -> str:
        return f'''<{self.__class__.__name__}: \n    {"""
    """.join([f"{obj} = {val}" for obj, val in self.__dict__.items()])}\n>'''
    # triple quotes here make this work with py 3.10 lol
    # TODO: do this better lol
    # also black doesnt like this lmao, so uhhhhhhh