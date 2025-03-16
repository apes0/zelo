import logging
from logging import CRITICAL, DEBUG, ERROR, FATAL, INFO, WARN, WARNING

logger = logging.getLogger('zelo')
formatter = logging.Formatter('%(levelname)-8s %(message)s')
streamHandler = logging.StreamHandler()
logger.addHandler(streamHandler)
streamHandler.setFormatter(formatter)

logger.setLevel(logging.ERROR)

# debbuger config
# contains lables for each thing that we can debug

# ? why do i keep these in a dict lol?
cfg = {
    'all': False,  # if we should log everything
    'events': False,  # event triggerings
    'evErrors': True,  # event errors
    'grab': False,  # and ungrab
    'press': False,  # and release
    'keys': False,  # key related logs
    'buttons': False,  # button related logs
    'focus': False,  # focus changes
    'drawable': False,  # basically anything from api/drawable.py
    'errors': True,  # backend errors
    'backend': False,  # backend debug info
    'windows': False,  # anything to do with windows
    'extensions': True,  # extension logs
    'others': True,  # anything else that's logging
}


def shouldLog(name: str | list[str], single=True):
    if isinstance(name, str):
        if not (cfg['all'] or cfg.get(name, cfg['others'])):
            return False

    elif isinstance(name, list):
        log = False
        for n in name:
            if cfg.get(n, cfg['others']):
                log = True
                break
            elif not single:
                return False

        if not log:
            return False

    else:
        return False

    return True


def _log(name: str | list[str], level: int, message: str):
    if isinstance(name, list):
        name = ', '.join(name)
    logger.log(level, f'{name}: {message}')


def log(name: str | list[str], level: int, message: str, single=True):
    if shouldLog(name, single):
        _log(name, level, message)
