from typing import Callable
from .pres import Pre
from .ctx import Ctx
import os
import importlib
import traceback
from typing import TYPE_CHECKING
import trio


async def catch(fn: Callable, err: str, *args) -> tuple[bool, BaseException | None]:
    try:
        await fn(*args)
        return False, None
    except BaseException as e:
        print(f'{err}: {traceback.format_exc()}')
        return True, e


tests: list['Test'] = []

# FIXME: we shouldn't run pres if any of them are shared and in the same order between tests


class Test:
    def __init__(self, lable: str, pres: list[Pre], test: Callable, sname: str):
        self.lable = f'{sname}/{lable}'
        self._lable = lable
        self.pres = pres
        self._test = test
        self.sname = sname
        tests.append(self)

    async def test(self, nurs: 'trio.Nursery') -> tuple[bool, BaseException | None]:
        print(f'starting test {self.lable}')
        ctx = Ctx(nurs)
        ctx.pres = [pre() for pre in self.pres]
        for i, pre in enumerate(ctx.pres):
            print(f'\tstarting pre {pre.lable}')
            res, err = await catch(
                pre.run, f'\t{self.lable}: pre {pre.lable} failed', ctx
            )
            if res:
                await self.cleanUp(ctx, end=i)
                return False, err

        res, err = await catch(self._test, f'{self.lable} failed', ctx)
        if res:
            await self.cleanUp(ctx)
            return False, err

        print(f'{self.lable} succeeded!')
        await self.cleanUp(ctx)
        return True, None

    async def cleanUp(self, ctx: Ctx, end: int | None = None) -> None:
        for pre in reversed(ctx.pres[:end]):
            print(f'\tstopping {pre.lable}')
            await catch(
                pre.stop, f'\t{self.lable}: pre {pre.lable} failed to stop', ctx
            )
        print()


def test(lable, preq, tcase):
    def deco(fn):
        return Test(lable, preq, fn, tcase)

    return deco


def load(suit='', test='', igndirs=[], ignfiles=[]) -> None:
    dirname: str = os.path.dirname(__file__)
    for dir in os.listdir(dirname):
        cur: str = os.path.join(dirname, dir)
        if (
            dir.startswith('__')
            or dir.startswith('.')
            or os.path.isfile(cur)
            or not dir.endswith(suit)
            or dir in igndirs
        ):
            continue
        for file in os.listdir(cur):
            if (
                os.path.isdir(file)
                or file.startswith('__')
                or file.startswith('.')
                or not file[:-3].endswith(test)
                or file in ignfiles
            ):
                continue
            importlib.import_module(f'.{dir}.{file[:-3]}', package='tests')
