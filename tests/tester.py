from typing import Callable
import traceback
from .pres import Pre
import os
import importlib

def catch(fn, err):
    try:
        fn()
        return False
    except:
        print(f'{err}: \n{traceback.format_exc()}')
        return True

tests = []

class Test:
    def __init__(self, lable: str, preq: list[Pre], test: Callable):
        self.lable = lable
        self.preq = preq
        self._test = test
        self.success: bool = False
        tests.append(self)
    
    def test(self):
        for pre in self.preq:
            if catch(pre.start, f'Test {self.lable}: prerequesite {pre.lable} failed to start'):
                return

        if catch(self._test(), f'Test {self.lable} failed'):
            return

        for pre in self.preq:
            if catch(pre.stop, f'Test {self.lable}: prerequesite {pre.lable} failed to stop'):
                return
        
        self.success = True


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