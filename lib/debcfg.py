import logging
from logging import CRITICAL, DEBUG, ERROR, FATAL, INFO, WARN, WARNING

grey = ''
white = ''
yellow = ''
red = ''
bold = ''
boldRed = ''
reset = ''

try:
    import colorama

    grey = colorama.Fore.LIGHTBLACK_EX
    white = colorama.Fore.WHITE
    yellow = colorama.Fore.YELLOW
    red = colorama.Fore.RED
    bold = colorama.Style.BRIGHT
    boldRed = bold + red
    reset = colorama.Fore.RESET + colorama.Style.RESET_ALL
except:
    pass

fmt = '{col}%(levelname)-8s{reset} %(message)s'


class Formatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        log_fmt = {
            logging.DEBUG: fmt.format(col=grey, reset=reset),
            logging.INFO: fmt.format(col=white, reset=reset),
            logging.WARNING: fmt.format(col=yellow, reset=reset),
            logging.ERROR: fmt.format(col=red, reset=reset),
            logging.CRITICAL: fmt.format(col=boldRed, reset=reset + bold),
        }.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger('zelo')
streamHandler = logging.StreamHandler()
logger.addHandler(streamHandler)
streamHandler.setFormatter(Formatter())

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
    'errors': False,  # backend errors
    'backend': True,  # backend debug info
    'windows': False,  # anything to do with windows
    'extensions': False,  # extension logs
    'startSoon': True,  # stuff erroring in start soon calls
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
