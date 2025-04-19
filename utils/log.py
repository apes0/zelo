import logging


logger = logging.getLogger('zelo')


formatter = logging.Formatter('%(levelname)-8s %(message)s')


def log(file: str, level: int = logging.DEBUG):
    logger.setLevel(level)
    fileHandler = logging.FileHandler(file)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)


def logTerm(level: int = logging.DEBUG):
    logger.setLevel(level)
