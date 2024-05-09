import logging

logger = logging.getLogger('zelo')
formatter = logging.Formatter('%(levelname)-8s %(message)s')
streamHandler = logging.StreamHandler()
logger.addHandler(streamHandler)
streamHandler.setFormatter(formatter)

# debbuger config
# contains lables for each thing that we can debug

cfg = {
    'all': False,  # if we should log everything
    'events': False,  # event triggerings
    'evErrors': False, # event errors
    'grab': False,  # and ungrab
    'press': False,  # and release
    'errors': False,  # backend errors
    'backend': False,  # backend debug info
    'windows': False,  # anything to do with windows
    'extensions': False,  # extension logs
    'others': False,  # anything else that's logging
}


# TODO: multiple filters
def log(name: str, level: int, message: str):
    if cfg['all'] or cfg.get(name, cfg['others']):
        logger.log(level, f'{name}: {message}')
