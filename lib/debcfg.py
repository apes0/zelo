import logging

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
    'errors': True,  # backend errors
    'backend': False,  # backend debug info
    'windows': False,  # anything to do with windows
    'extensions': False,  # extension logs
    'others': True,  # anything else that's logging
}


def log(name: str | list[str], level: int, message: str, single=True):
    if isinstance(name, str):
        if not (cfg['all'] or cfg.get(name, cfg['others'])):
            return

    elif isinstance(name, list):
        log = False
        for n in name:
            if cfg.get(n, cfg['others']):
                log = True
                break
            elif not single:
                return

        if not log:
            return

        name = ', '.join(name)

    else:
        return

    logger.log(level, f'{name}: {message}')
