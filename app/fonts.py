#!/usr/bin/env python

import logging
import coloredlogs

# logger
formatter = '%(levelname)s: line %(lineno)d in %(funcName)s, %(filename)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, format=formatter)
logger = logging.getLogger('fonts')
coloredlogs.install(level='DEBUG')


CHAR_MAP_WIDTH = 5
CHAR_MAP_HEIGHT = 7
CHAR_MAX_POINTS_NUM = 20
CHAR_MIN_POINTS_NUM = 11

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


# font data, [a-z], 5x7
CHAR_MAP = {
    'a': """
    _***_
    *...*
    *...*
    *****
    *...*
    *...*
    *...*
    """,

    'b':"""
    ****.
    *...*
    *...*
    ****.
    *...*
    *...*
    ****.
    """,

    'c': """
    _***_
    *...*
    *..._
    *..._
    *..._
    *...*
    _***_
    """,

    'd': """
    ****.
    *.._*
    *...*
    *...*
    *...*
    *...*
    ****_
    """,

    'e': """
    *****
    *..._
    *....
    *****
    *....
    *....
    *****
    """,

    'f': """
    *****
    *.._.
    *....
    ****_
    *....
    *....
    *____
    """,

    'g': """
    _***_
    *...*
    *....
    *.***
    *...*
    *...*
    _***.
    """,

    'h': """
    *___*
    *...*
    *...*
    *****
    *...*
    *...*
    *...*
    """,

    'i': """
    _***_
    ..*..
    ..*_.
    __*__
    ..*..
    ..*..
    _***_
    """,

    'j': """
    ____*
    ....*
    ____*
    ....*
    *...*
    _*..*
    ..**_
    """,

    'k': """
    *...*
    *..*_
    *.*_.
    **___
    *.*..
    *..*_
    *...*
    """,

    'l': """
    *....
    *____
    *....
    *____
    *..._
    *....
    *****
    """,

    'm': """
    *...*
    **_**
    *_*_*
    *...*
    *...*
    *...*
    *...*
    """,

    'n': """
    *...*
    **..*
    *.*.*
    *_*.*
    *.*.*
    *..**
    *...*
    """,

    'o': """
    _***_
    *...*
    *...*
    *...*
    *...*
    *...*
    _***_
    """,

    'p': """
    ****_
    *...*
    *...*
    ****_
    *....
    *....
    *___.
    """,

    'q': """
    .***.
    *...*
    *...*
    *...*
    *_*_*
    *..*_
    .**.*
    """,

    'r': """
    ****_
    *...*
    *...*
    ****_
    *...*
    *...*
    *...*
    """,

    's': """
    .***_
    *...*
    *....
    _***_
    ....*
    *...*
    _***_
    """,

    't': """
    *****
    ..*..
    ..*..
    __*__
    __*__
    ._*..
    ..*..
    """,

    'u': """
    *...*
    *...*
    *...*
    *___*
    *...*
    *...*
    _***_
    """,

    'v': """
    *...*
    *._.*
    *._.*
    _*_*_
    .*_*.
    .*_*.
    ..*..
    """,

    'w': """
    *...*
    *._.*
    *._.*
    *.*.*
    .*_*.
    .*_*.
    .*_*.
    """,

    'x': """
    *...*
    *._.*
    .*_*.
    ._*_.
    .*_*.
    *_._*
    *...*
    """,

    'y': """
    *...*
    *._.*
    .*_*.
    __*__
    ..*..
    __*__
    ..*..
    """,

    'z': """
    *****
    ....*
    .._*_
    ._*_.
    _*...
    *....
    *****
    """,
}
