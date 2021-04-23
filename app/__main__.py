#!/usr/bin/env python

from . unlabeled_mapf_solver import Unlabled_MAPF_Solver
from . fonts import create_transition_file, get_trimed_str, CHAR_MAP_WIDTH
import logging
import eel
import json
import requests
import os

# set logger
logger = logging.getLogger(__name__)
formatter = '%(levelname)s: line %(lineno)d in %(funcName)s, %(filename)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, format=formatter)

@eel.expose
def key_pressed(before_pos, next_char, ins_cnt):
    """called from gui app

    Args
    - before_pos (list of integer): before
    - next_char (char): after
    - ins_cnt (int): #(instances)

    Returns
    - dictionary
      - solution: plan of agents
      - char: final config
    """
    logger.info(f'solve unlabeled-MAPF to char-{next_char}')
    ins_name = f'./instance/tmp/{ins_cnt}.txt'
    plan_name = f'./instance/tmp/{ins_cnt}.json'
    map_name = './map/3x4.map'
    create_transition_file(ins_name, before_pos, next_char)
    solver = Unlabled_MAPF_Solver(map_name, ins_name)
    solver.solve()

    # create toio instructions
    toio_plan = []
    for config in solver.solution:
        toio_plan.append([ {"x": i % CHAR_MAP_WIDTH, "y": int(i / CHAR_MAP_WIDTH)}
                           for i in config ])
    with open(plan_name, mode='w') as f:
        json.dump(toio_plan, f, indent=2)
    plan_full_path = os.path.join(os.getcwd(), plan_name)
    try:
        requests.get(f"http://localhost:3000{plan_full_path}")
    except:
        logger.warning(f"server seems to be down now")

    return {
        "solution": solver.solution,
        "char": get_trimed_str(next_char)
    }

if __name__ == '__main__':
    eel.init("gui", allowed_extensions=[".js", ".html"])
    eel.start("index.html",
              host="localhost",
              port=8000,
              mode="chrome")
