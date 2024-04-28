from typing import Callable
from .pres import Pre
import os
import importlib
from typing import TYPE_CHECKING
import trio

async def catch(fn: Callable, err: str, *args) -> bool:
    try:
        await fn(*args)
        return False
    except BaseException as e:
        print(f'{err}: {e}')
        return True


tests: list['Test'] = []

# FIXME: we shouldn't run pres if any of them are shared and in the same order between tests

class Test:
    def __init__(self, lable: str, pres: list[Pre], test: Callable):
        self.lable = lable
        self.pres = pres
        self._test = test
        tests.append(self)

    async def test(self, nurs: 'trio.Nursery') -> bool:
        for i, pre in enumerate(self.pres):
            if await catch(pre.run, f'{self.lable}: {pre.lable} failed', nurs):
                await self.cleanUp(nurs, end=i)
                return False

        if await catch(self._test, f'{self.lable} failed', self):
            await self.cleanUp(nurs)
            return False

        print(f'{self.lable} succeeded!')
        await self.cleanUp(nurs)
        return True

    async def cleanUp(self, nurs: 'trio.Nursery', end: int|None = None) -> None:
        for pre in reversed(self.pres[:end]):
            await catch(pre.stop, f'{self.lable}: {pre.lable} failed to stop', nurs)

class Shared:
    mul = 1
    def __init__(self, pres: list[Pre]) -> None:
        self.pres = pres
        self.shares = 0
        self.started = False

        async def start(_pre: Pre, nurs: trio.Nursery, done: trio.Event):
            if self.started:
                done.set()
                return

            self.started = True

            _pre.data = []
            
            for pre in self.pres:
                await pre.run(nurs)
                _pre.data.append(pre.data)

            done.set()

        async def end(pre: Pre, nurs: trio.Nursery, done: trio.Event):
            self.shares -= 1

            if self.shares != 0:
                done.set()
                return

            for pre in self.pres:
                await pre.stop(nurs)

            done.set()

        new = Pre(','.join([pre.lable for pre in pres]), start)
        new.end = end
        self.new = new
    
    def __call__(self, test: Test):
        self.shares += self.__class__.mul
        test.pres = [self.new, *test.pres]

def test(lable, preq):
    def deco(fn):
        return Test(lable, preq, fn)

    return deco


def load() -> None:
    dirname: str = os.path.dirname(__file__)
    for dir in os.listdir(dirname):
        cur: str = os.path.join(dirname, dir)
        if dir.startswith('__') or os.path.isfile(cur):
            continue
        for file in os.listdir(cur):
            if os.path.isdir(file) or file.startswith('__'):
                continue
            importlib.import_module(f'.{dir}.{file[:-3]}', package='tests')
