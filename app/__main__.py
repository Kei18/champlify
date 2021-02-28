#!/usr/bin/env python

from . unlabeled_mapf_solver import Unlabled_MAPF_Solver
from . fonts import get_config_from_char

if __name__ == '__main__':
    config_from = get_config_from_char('a')
    config_to = get_config_from_char('b')

    with open('./instance/tmp.ins', 'w') as f:
        for s, g in zip(config_from, config_to):
            f.write('{},{},{},{}\n'.format(s[0], s[1], g[0], g[1]))

    map_name = './map/5x7.map'
    ins_name = './instance/tmp.ins'
    # map_name = './map/toy.map'
    # ins_name = './instance/toy.ins'

    solver = Unlabled_MAPF_Solver(map_name, ins_name)
    solver.solve()
    print(solver.solution)
