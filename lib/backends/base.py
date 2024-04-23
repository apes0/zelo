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
