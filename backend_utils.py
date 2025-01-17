"""
frequently used utils for the backend of the bot
"""

import pickle


def ordinal(n):
    """
    Convert an integer into its ordinal representation::

        make_ordinal(0)   => '0th'
        make_ordinal(3)   => '3rd'
        make_ordinal(122) => '122nd'
        make_ordinal(213) => '213th'
    """
    n = int(n)
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix


def genitive(word):
    word = word.strip()
    return f"{word}'" if word.endswith('s') else f"{word}'s"


def map_values(val: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
    """
    maps a value in a range to another range
    """
    val = min(max(val, in_min), in_max)
    return (val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def load_cache(path, name, logger):
    """
    loads cache located in the specified directory into memory,
    and creates an empty one if not valid.
    """
    try:
        with open(path, 'rb') as cache_file:
            obj = pickle.load(cache_file)
            logger.info(f'successfully deserialized "{name}"')
            return obj
    except (FileNotFoundError, EOFError):
        logger.warning(f'could not deserialize "{name}"! creating empty cache.')
        open(path, 'wb').close()
        return {}


def load_token(path, name, logger):
    """
    returns token from a given token location, and raises an error if not valid.
    """
    try:
        with open(path, 'r', encoding='utf-8') as info_file:
            temp = info_file.readlines()
            if not temp:
                raise EOFError
            logger.info(f'successfully read "{name}"')
            return [x.strip() for x in temp]
    except (FileNotFoundError, EOFError) as token_error:
        logger.fatal(f'token "{name}" not found!')
        raise token_error


def save_caches(caches, caches_locations, logger, cog_name):
    for cache, cache_path in caches_locations.items():
        with open(cache_path, 'wb') as cache_file:
            pickle.dump(caches[cache], cache_file)
    logger.debug(f'successfully serialized all caches for {cog_name}.')


class LogManager:
    def __init__(self, logger, level, title, width):
        self.logger = logger
        self.level = level
        self.title = title.upper()
        self.width = width

    def __enter__(self):
        self.logger.log(self.level, f'> START OF {self.title} <'.center(self.width, '='))

    def __exit__(self, *args):
        self.logger.log(self.level, f'> END OF {self.title} <'.center(self.width, '='))
