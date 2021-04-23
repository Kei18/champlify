#!/usr/bin/env python

import logging
import coloredlogs

# logger
formatter = '%(levelname)s: line %(lineno)d in %(funcName)s, %(filename)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, format=formatter)
logger = logging.getLogger('fonts')
coloredlogs.install(level='DEBUG')


CHAR_MAP_WIDTH = 3
CHAR_MAP_HEIGHT = 4
CHAR_MAX_POINTS_NUM = 6
CHAR_MIN_POINTS_NUM = 6

def get_config_from_char(c):
    """translate char to config

    Args:
    - c (char): char

    Returns
    - list: (s, g), config
    """
    config = []
    if c not in CHAR_MAP.keys():
        return config

    # trimming
    line = get_trimed_str(c)
    for i, s in enumerate(line):
        if s in ['*', '_']:
            config.append((i % CHAR_MAP_WIDTH, int(i / CHAR_MAP_WIDTH)))
    return config

def create_transition_file(filename, before_pos, c_to):
    """create input file for unlabeled MAPF solver

    Args:
    - filename (string): output file
    - before_pos (list of integer): before
    - c_to (char): after
    """
    config_to = get_config_from_char(c_to)
    with open(filename, 'w') as f:
        for s, g in zip(before_pos, config_to):
            f.write('{},{},{},{}\n'.format(int(s)%CHAR_MAP_WIDTH, int(s)//CHAR_MAP_WIDTH, g[0], g[1]))

def get_trimed_str(c):
    """translate char to string

    Args:
    - c (char)

    Returns
    - string
    """
    return CHAR_MAP[c].strip().replace('\n', '').replace(' ', '')


# font data, [a-z], 3x4
CHAR_MAP = {
    'f': """
    **.
    *..
    **.
    *..
    """,

    'j': """
    ..*
    ..*
    *.*
    .**
    """,

    'l': """
    *..
    *..
    *..
    ***
    """,

    'o': """
    .*.
    *.*
    *.*
    .*.
    """,

    't': """
    ***
    .*.
    .*.
    .*.
    """,

    'y': """
    *.*
    *.*
    .*.
    .*.
    """,
}
