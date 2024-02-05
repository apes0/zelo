from lib.extension import Extension
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from lib.ctx import Ctx


class Log(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.file: str
        self.level: int = logging.DEBUG

        super().__init__(ctx, cfg)

        logging.basicConfig(filename=self.file, encoding='utf-8', level=self.level)
