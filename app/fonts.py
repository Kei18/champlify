#!/usr/bin/env python

CHAR_MAP_WIDTH = 5
CHAR_MAP_HEIGHT = 7
CHAR_MAX_POINTS_NUM = 20
CHAR_MIN_POINTS_NUM = 11

def get_config_from_char(c):
    """
    Returns
    - list: (s, g)
    """
    config = []
    line = CHAR_MAP[c].strip().replace('\n', '').replace(' ', '')
    for i, s in enumerate(line):
        if s in ['*', '_']:
            config.append((i % CHAR_MAP_WIDTH, int(i / CHAR_MAP_WIDTH)))
    return config



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
    .***.
    *...*
    *....
    *....
    *....
    *...*
    .***.
    """
}
