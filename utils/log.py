import logging


def log(file: str, level: int = logging.DEBUG):
    logging.basicConfig(filename=file, encoding='utf-8', level=level)
