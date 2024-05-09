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
    except AssertionError as e: # let the rest bubble down
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
        print(f'starting test {self.lable}')
        for i, pre in enumerate(self.pres):
            print(f'\tstarting pre {pre.lable}')
            if await catch(pre.run, f'\t{self.lable}: pre {pre.lable} failed', nurs):
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
            print(f'\tstopping {pre.lable}')
            await catch(pre.stop, f'\t{self.lable}: pre {pre.lable} failed to stop', nurs)
        print()

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

        async def end(_pre: Pre, nurs: trio.Nursery, done: trio.Event):
            self.shares -= 1

            if self.shares != 0:
                done.set()
                return

            for pre in self.pres:
                await pre.stop(nurs)

            done.set()

        new = Pre(', '.join([pre.lable for pre in pres]), start)
        new.end = end
        self.new = new
    
    def __call__(self, test: Test):
        self.shares += self.__class__.mul
        test.pres = [self.new, *test.pres]

def test(lable, preq):
    def deco(fn):
        return Test(lable, preq, fn)

    return deco


def load(suit='', test='') -> None:
    dirname: str = os.path.dirname(__file__)
    for dir in os.listdir(dirname):
        cur: str = os.path.join(dirname, dir)
        if dir.startswith('__') or dir.startswith('.') or os.path.isfile(cur) or not dir.endswith(suit):
            continue
        for file in os.listdir(cur):
            if os.path.isdir(file) or file.startswith('__') or file.startswith('.') or not file[:-3].endswith(test):
                continue
            importlib.import_module(f'.{dir}.{file[:-3]}', package='tests')
