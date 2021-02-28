#!/usr/bin/env python

import os
import sys
import logging
import coloredlogs
from itertools import product
import queue

from . loader import *

import amplify
from amplify import sum_poly
from amplify.constraint import equal_to, less_equal
from amplify.client import FixstarsClient

# logger
formatter = '%(levelname)s: line %(lineno)d in %(funcName)s, %(filename)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, format=formatter)
logger = logging.getLogger('Unlabled_MAPF_Solver')
coloredlogs.install(level='DEBUG')


class Unlabled_MAPF_Solver:
    """
    """

    def __init__(self, map_name, ins_name, timeout=1000, max_makespan=50):
        self.field = load_map(map_name)
        self.instance = load_instance(ins_name, self.field)
        self.used_edges = None
        self.solution = None
        self.makespan = self.get_minimum_makespan()
        self.timeout = timeout
        self.max_makespan = max_makespan
        self.DIST_TABLE_FROM_STARTS = []
        self.DIST_TABLE_FROM_GOALS = []

        # compute distance from starts/goals
        self.set_dist_table()

        # simple error check
        if 'TOKEN' not in os.environ:
            logger.error("make .env and register your token")
            sys.exit()
        if self.instance['agents'] == 0:
            logger.error("invalid instance file")
            sys.exit()

    def solve(self):
        """try solve the instance, gradually incrementing makespan
        """

        logger.info("find feasible solution")

        # special case
        if sorted(self.instance["starts"]) == sorted(self.instance["goals"]):
            logger.info("starts and goals are euqal")
            self.solution = [ self.instance["starts"] ]
            return

        while True:
            logger.info(f"try to find a solution with makespan={self.makespan}")
            try:
                self.find_feasible_solution()
            except:
                logger.warning(f"failed to find a feasible solution with makespan={self.makespan}")

            if self.makespan >= self.max_makespan:
                logger.info("failed to solve the instance")
                return
            if self.used_edges is None:
                self.makespan += 1
            else:
                # solved
                logger.info(f"solved, makespan={self.makespan}")
                break
        logger.info("translate a set of locations to a set of paths")
        self.set_solution()
        # check consistency
        if not self.validate_solution():
            logger.error("invalid solution")
            sys.exit()

    def find_feasible_solution(self):
        """find a feasible locations with makespan, found -> set self.used_edges
        """
        # create variables
        q = []
        index = 0
        for t in range(self.makespan):
            q.append([])
            for v in range(self.field["size"]):
                l = len(self.field["adj"][v])+1
                q[-1].append(
                    amplify.gen_symbols( amplify.BinaryPoly, index, (1, l) )
                )
                index += l

        # set starts
        constraints_starts = [
            equal_to(sum_poly( q[0][v][0] ), 1)
            for v in self.instance["starts"]
        ]

        for v in range(self.field["size"]):
            if v in self.instance["starts"]:
                continue
            for i in range(len(q[0][v][0])):
                q[0][v][0][i] = amplify.BinaryPoly(0)

        # set goals
        constraints_goals = [
            equal_to(sum_poly([ q[-1][u][0][ self.field["adj"][u].index(v) ]
                                for u in self.field["adj"][v] ] +
                              [ q[-1][v][0][ len(self.field["adj"][v]) ] ]),
                     1)
            for v in self.instance["goals"]
        ]

        for v in range(self.field["size"]):
            for i in range(len(self.field["adj"][v])):
                if self.field["adj"][v][i] not in self.instance["goals"]:
                    q[-1][v][0][i] = amplify.BinaryPoly(0)
            if v not in self.instance["goals"]:
                q[-1][v][0][-1] = amplify.BinaryPoly(0)

        # upper bound, in
        constraints_in = [
            less_equal(sum_poly([ q[t][u][0][ self.field["adj"][u].index(v) ]
                                  for u in self.field["adj"][v] ] +
                                [ q[t][v][0][ len(self.field["adj"][v]) ] ]),
                       1)
            for v, t in product(range(self.field["size"]), range(0, self.makespan-1))
        ]

        # upper bound, out
        constraints_out = [
            less_equal(sum_poly( q[t][v][0] ),
                       1)
            for v, t in product(range(self.field["size"]), range(1, self.makespan))
        ]

        # continuity
        constraints_continuity = [
            equal_to(sum_poly([ q[t][u][0][ self.field["adj"][u].index(v) ]
                                for u in self.field["adj"][v] ] +
                              [ q[t][v][0][ len(self.field["adj"][v]) ] ])
                     -
                     sum_poly( q[t+1][v][0] ),
                     0)
            for v, t in product(range(self.field["size"]), range(0, self.makespan-1))
        ]

        # branching
        for v in range(self.field["size"]):
            if not self.field["body"][v]:
                continue
            # unreachable vertexes from starts
            for t in range(0, min(self.DIST_TABLE_FROM_STARTS[v], self.makespan)):
                for i in range(len(q[t][v][0])):
                    q[t][v][0][i] = amplify.BinaryPoly(0)
            # unreachable vertexes to goals
            for t in range(max(self.makespan - self.DIST_TABLE_FROM_GOALS[v] + 1, 0), self.makespan):
                for i in range(len(q[t][v][0])):
                    q[t][v][0][i] = amplify.BinaryPoly(0)

        # set occupied vertex
        for v in range(self.field["size"]):
            if self.field["body"][v]:
                continue
            for t in range(0, self.makespan):
                q[t][v][0][-1] = amplify.BinaryPoly(0)

        # create model
        model = sum(constraints_starts)
        model += sum(constraints_goals)
        if len(constraints_in) > 0:
            model += sum(constraints_in)
        if len(constraints_out) > 0:
            model += sum(constraints_out)
        if len(constraints_continuity):
            model += sum(constraints_continuity)

        # setup client
        client = FixstarsClient()
        client.token = os.environ['TOKEN']
        client.parameters.timeout = self.timeout

        # solve
        solver = amplify.Solver(client)
        result = solver.solve(model)
        if len(result) > 0:
            self.used_edges = amplify.decode_solution(q, result[0].values)

    def get_minimum_makespan(self):
        """compute the minimum makesapn for solutions (max min)

        Returns
        - int
        """
        return max([ self.get_dist_table([s], lambda n: n in self.instance["goals"])[0]
                     for s in self.instance["starts"] ])

    def set_dist_table(self):
        """set distance table
        """
        logger.info("preprocessing, create distance table")
        _, self.DIST_TABLE_FROM_STARTS = self.get_dist_table(self.instance["starts"])
        _, self.DIST_TABLE_FROM_GOALS  = self.get_dist_table(self.instance["goals"])

    def get_dist_table(self, init_locations, check_termination=None):
        """used in set_dist_table, get_minimum_makespan

        Returns:
        - distance when finishing the search
        - list[node_index]
        """
        # initialize
        dist_table = [ self.field["size"] ] * self.field["size"]

        # set initial OPEN list
        OPEN = queue.Queue()
        for v in init_locations:
            dist_table[v] = 0
            OPEN.put(v)

        # main loop
        while not OPEN.empty():
            n = OPEN.get()
            d_n = dist_table[n]

            # check termination
            if check_termination != None and check_termination(n):
                break

            # expand neighbors
            for m in self.field["adj"][n]:
                if d_n + 1 >= dist_table[m]:
                    continue
                dist_table[m] = d_n + 1
                OPEN.put(m)

        return d_n, dist_table

    def set_solution(self):
        """
        """
        if self.used_edges is None:
            logger.warning("this instance is not solved yet")
            return

        self.solution = [ self.instance["starts"] ]
        for t in range(len(self.used_edges)):
            config = []
            for v_from in self.solution[-1]:
                i = self.used_edges[t][v_from][0].index(1)
                if i == len(self.used_edges[t][v_from][0]) - 1:
                    v_to = v_from
                else:
                    v_to = self.field["adj"][v_from][i]
                config.append(v_to)
            self.solution.append(config)

        # check swap conflicts
        for t in range(1, len(self.solution)):
            for i in range(self.instance["agents"]):
                for j in range(i+1, self.instance["agents"]):
                    if self.solution[t-1][i] == self.solution[t][j] and\
                       self.solution[t][i] == self.solution[t-1][j]:
                        # swap rest of paths
                        for _t in range(t, len(self.solution)):
                            val = self.solution[_t][i]
                            self.solution[_t][i] = self.solution[_t][j]
                            self.solution[_t][j] = val

    def validate_solution(self):
        """
        Returns
        - Boolean
        """
        if self.solution is None:
            logger.warning("solution is not found")
            return False
        # check starts
        if sorted(self.solution[0]) != sorted(self.instance["starts"]):
            logger.warning("invalid starts")
            return False
        # check goals
        if sorted(self.solution[-1]) != sorted(self.instance["goals"]):
            logger.warning("invalid goals")
            return False
        for t in range(1, len(self.solution)):
            for i in range(self.instance["agents"]):
                # check continuity
                if self.solution[t][i] != self.solution[t-1][i] and\
                   self.solution[t][i] not in self.field["adj"][self.solution[t-1][i]]:
                    logger.warning("the path is invalid")
                    return False
                for j in range(i+1, self.instance["agents"]):
                    # check vertex conflicts
                    if self.solution[t][i] == self.solution[t][j]:
                        logger.warning("there is a vertex conflict")
                        return False
                    # check swap conflicts
                    if self.solution[t-1][i] == self.solution[t][j] and\
                       self.solution[t][i] == self.solution[t-1][j]:
                        logger.warning("there is a swap conflict")
                        return False
        return True
