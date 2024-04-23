import subprocess
from typing import Callable, Any
import os
import time

# these are all the prerequesites, they should only block until they can be used

class Pre:
    def __init__(self, lable: str, start: Callable[[], Any], end: Callable[[Any], None]) -> None:
        self.lable = lable
        self.start = start
        self.end = end
        self.data: Any
    
    def run(self):
        self.data = self.start()
    
    def stop(self):
        self.end(self.data)

startX = Pre(
    'Starting X', lambda: subprocess.call(
        f'Xephyr +extension RANDR +xinerama -ac -br -screen 600x400 :{str(int(os.environ["DISPLAY"][1:]) + 1)}'.split(' ')
    ) or time.sleep(2),
    lambda data: os.kill(data, 8)
)