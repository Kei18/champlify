#!/usr/bin/env python

import re

def load_map(map_name):
    """load map file

    Args:
    - map_name (string): file name

    Returns:
    - dictionary
      - width (int)
      - height (int)
      - size (int): width*height
      - body (list[node_index], boolean): true -> free, false -> obstacle (@ or T)
      - adj (list[node_index], list of indexes): neighbor nodes
    """
    r_height = re.compile(r"height\s(\d+)")
    r_width = re.compile(r"width\s(\d+)")
    r_map = re.compile(r"map")

    # wheter to load body or not
    on_load_map_body = False

    width = 0
    height = 0
    body = []
    adj = []

    with open(map_name) as f:
        for row in f:
            # set vertex
            if on_load_map_body:
                for s in row.strip():
                    body.append( False if s in [ "@", "T" ] else True )
                continue
            # set height/width
            m = re.match(r_height, row)
            if m:
                height = int(m.group(1))
                continue
            m = re.match(r_width, row)
            if m:
                width = int(m.group(1))
                continue
            # start loading body
            if re.match(r_map, row):
                on_load_map_body = True

    # set adjacency
    if len(body) == width*height:
        for i, vertex in enumerate(body):
            # obstacle
            if not vertex:
                adj.append([])
                continue
            neigh = []
            # up
            if i >= width and body[i-width]:
                neigh.append(i-width)
            # down
            if i + width < width*height and body[i+width]:
                neigh.append(i+width)
            # left
            if i % width != 0 and body[i-1]:
                neigh.append(i-1)
            # right
            if (i+1) % width != 0 and body[i+1]:
                neigh.append(i+1)
            adj.append(neigh)

    return {
        "width": width,
        "height": height,
        "size": width*height,
        "body": body,
        "adj": adj
    }


def load_instance(instance_name, field):
    """ load instance file

    Args:
    - instance_name (string): file name
    - field (dictionary): see load_map

    Returns:
    - dictionary
      - agents (int)
      - starts (list of node indexes)
      - goals (list of node indexes)
    """

    r_loc = re.compile(r"(\d+),(\d+),(\d+),(\d+)")

    agents = 0
    starts = []
    goals = []

    with open(instance_name) as f:
        for row in f:
            m = re.match(r_loc, row)
            if m:
                s = field["width"] * int(m.group(2)) + int(m.group(1))  # start
                g = field["width"] * int(m.group(4)) + int(m.group(3))   # goal
                if field["body"][s] and field["body"][g]:
                    starts.append(s)
                    goals.append(g)

    return {
        "agents": len(starts),
        "starts": starts,
        "goals": goals
    }
