from typing import Callable
from .pres import Pre
import os
import importlib

# TODO: aaaaaa i need typing 

async def catch(fn, err, *args):
    try:
        await fn(*args)
        return False
    except BaseException as e:
        print(f'{err}: {e}')
        return True

tests = []

class Test:
    def __init__(self, lable: str, preq: list[Pre], test: Callable):
        self.lable = lable
        self.preq = preq
        self._test = test
        tests.append(self)
    
    async def test(self, nurs):
        for i, pre in enumerate(self.preq):
            if await catch(pre.run, f'{self.lable}: {pre.lable} failed', nurs):
                await self.cleanUp(nurs, end=i)
                return False

        if await catch(self._test, f'{self.lable} failed', self):
            await self.cleanUp(nurs)
            return False
        
        print(f'{self.lable} succeeded!')
        await self.cleanUp(nurs)
        return True

    async def cleanUp(self, nurs, end=-1):
        for pre in reversed(self.preq[:end]):
            await catch(pre.stop, f'{self.lable}: {pre.lable} failed to stop', nurs)

def test(lable, preq):
    def deco(fn):
        return Test(lable, preq, fn)
    
    return deco

def load():
    dirname = os.path.dirname(__file__)
    for dir in os.listdir(dirname):
        cur = os.path.join(dirname, dir)
        if dir.startswith('__') or os.path.isfile(cur):
            continue
        for file in os.listdir(cur):
            if os.path.isdir(file) or file.startswith('__'):
                continue
            importlib.import_module(f'.{dir}.{file[:-3]}', package='tests')