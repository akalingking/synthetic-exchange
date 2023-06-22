import logging

from .position import Position
from .random_normal import RandomNormal
from .random_uniform import RandomUniform
from .strategy import Strategy


def create_strategy(*args, **kwargs):
    retval = None
    name = kwargs.get("name")
    if name == "RandomUniform":
        retval = RandomUniform(*args, **kwargs)
    elif name == "RandomNormal":
        retval = RandomNormal(*args, **kwargs)
    else:
        logging.error(f"invalid strategy: {name}")
    return retval
