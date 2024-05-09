import logging

from lib.debcfg import formatter

logger = logging.getLogger('zelo')

def log(file: str, level: int = logging.DEBUG):
    logger.setLevel(level)
    fileHandler = logging.FileHandler(file)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)

def logTerm(level: int = logging.DEBUG):
    logger.setLevel(level)
