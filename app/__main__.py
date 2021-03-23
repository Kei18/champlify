#!/usr/bin/env python

from . unlabeled_mapf_solver import Unlabled_MAPF_Solver
from . fonts import create_transition_file, get_trimed_str
import logging
import eel

# set logger
logger = logging.getLogger(__name__)
formatter = '%(levelname)s: line %(lineno)d in %(funcName)s, %(filename)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, format=formatter)


@eel.expose
def key_pressed(before_pos, next_char, ins_cnt):
    logger.info(f'solve unlabeled-MAPF to char-{next_char}')
    ins_name = f'./instance/tmp/{ins_cnt}.txt'
    map_name = './map/5x7.map'
    create_transition_file(ins_name, before_pos, next_char)
    solver = Unlabled_MAPF_Solver(map_name, ins_name)
    solver.solve()
    return {
        "solution": solver.solution,
        "char": get_trimed_str(next_char)
    }

if __name__ == '__main__':

    # map_name = './map/5x7.map'

    # create_transition_file(ins_name, 'a', 'b')

    # solver = Unlabled_MAPF_Solver(map_name, ins_name)
    # solver.solve()
    # print(solver.solution)

    eel.init("gui", allowed_extensions=[".js", ".html"])
    eel.start("index.html",
              host="localhost",
              port=8000,
              mode="chrome")
