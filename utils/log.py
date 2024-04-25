import logging

logger = logging.getLogger('zelo')

def log(file: str, level: int = logging.DEBUG):
    logger.setLevel(level)
    fileHandler = logging.FileHandler(file)
    logger.addHandler(fileHandler)

def logTerm(level: int = logging.DEBUG):
    logger.setLevel(level)
