from typing import Any

from _cffi_backend import _CDataBase

# TODO: move Ptr[], CPtr, void and enum to here


def parseArgs(*args) -> list[Any]:
    #    print(args)
    #    import inspect, os, colorama; stack = inspect.stack(); whiteSpace = len(stack); print(*((lines:=[f'{" "*(whiteSpace := whiteSpace - 1)}L {colorama.Fore.GREEN}{x.function}{colorama.Style.RESET_ALL} | {os.path.basename(x.filename)}:{x.lineno}\n' for x in stack]).reverse() or lines)) # noqa

    out = []

    for arg in args:
        if isinstance(arg, Base):
            out.append(arg.obj)
            continue

        out.append(arg)

    return out


class Base:
    def __init__(self, cast=True) -> None:
        self.obj: _CDataBase
        self.cast = cast

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, _CDataBase):
            return self.obj == __value
        return self.__dict__ == __value.__dict__

    def __getitem__(self, itm):
        obj = self.obj[itm]
        if not self.cast:
            return obj
        return self.__class__(obj)

    def __repr__(self) -> str:
        return f'''<{self.__class__.__name__}: \n    {"""
    """.join([f"{obj} = {val}" for obj, val in self.__dict__.items()])}\n>'''

    # triple quotes here make this work with py 3.10 lol
    # TODO: do this better lol


# some random types to get shit to work


class Ptr[T](Base):
    def __init__(self, obj: T):
        self.obj: T = obj
        super().__init__(cast=False)


type CPtr[T] = T

void = Ptr
