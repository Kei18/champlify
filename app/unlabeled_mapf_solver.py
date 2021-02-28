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
from amplify.constraint import equal_to, greater_equal
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
        self.locations = None
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

        logger.info("find feasible locations")
        while True:
            logger.info(f"try to find a solution with makespan={self.makespan}")
            try:
                self.find_feasible_locations()
            except:
                logger.warning("this instance maybe impossible to solve")
            if self.makespan >= self.max_makespan:
                logger.info("failed to solve the instance")
                return
            if not self.validate_locations():
                self.makespan += 1
            else:
                logger.info(f"solved, makespan={self.makespan}")
                logger.info("translate a set of locations to a set of paths")
                self.set_solution()
                break

    def find_feasible_locations(self):
        """find a feasible locations with makespan, found -> set self.locations
        """

        # special case
        if self.makespan == 0:
            # starts == goals
            self.locations = [[ int(v in self.instance["starts"]) for v in range(self.field["size"]) ]]
            return
        if self.makespan == 1:
            self.locations = []
            self.locations.append([ int(v in self.instance["starts"]) for v in range(self.field["size"]) ])
            self.locations.append([ int(v in self.instance["goals"]) for v in range(self.field["size"]) ])
            return

        # create variables
        q = amplify.gen_symbols(amplify.BinaryPoly, self.makespan+1, self.field["size"])

        # set starts and goals
        for v in range(self.field["size"]):
            q[0][v] = amplify.BinaryPoly(v in self.instance["starts"])
            q[self.makespan][v] = amplify.BinaryPoly(v in self.instance["goals"])

        # set occupied vertex
        for v in range(self.field["size"]):
            if self.field["body"][v]:
                continue
            for t in range(1, self.makespan):
                q[t][v] = amplify.BinaryPoly(0)

        # branching
        # Note: it is possible to merge constraints w.r.t. starts/goals
        for v in range(self.field["size"]):
            # unreachable vertexes from starts
            for t in range(1, min(self.DIST_TABLE_FROM_STARTS[v], self.makespan)):
                q[t][v] = BinaryPoly.amplify(0)
            # unreachable vertexes to goals
            for t in range(max(self.makespan - self.DIST_TABLE_FROM_GOALS[v] + 1, 1), self.makespan):
                q[t][v] = amplify.BinaryPoly(0)

        # create constraints
        # constraints w.r.t. the number of agents
        constraints_num_agents = [
            equal_to( sum_poly(q[t]), self.instance["agents"] ) for t in range(1, self.makespan)
        ]

        # constraints w.r.t. continuity, move to
        constraints_move_to = [
            greater_equal(
                sum_poly([ q[t+1][u] for u in (self.field["adj"][v] + [v]) ])  - q[t][v],
                0 )
            for t, v, in product(range(self.makespan), range(self.field["size"]))
        ]

        # constraints w.r.t. continuity, move from
        constraints_move_from = [
            greater_equal(
                sum_poly([ q[t-1][u] for u in (self.field["adj"][v] + [v]) ])  - q[t][v],
                0 )
            for t, v, in product(range(1, self.makespan+1), range(self.field["size"]))
        ]

        # create model
        model = sum(constraints_num_agents) + sum(constraints_move_to) + sum(constraints_move_from)

        # setup client
        client = FixstarsClient()
        client.token = os.environ['TOKEN']
        client.parameters.timeout = self.timeout

        # solve
        solver = amplify.Solver(client)
        result = solver.solve(model)
        if len(result) > 0:
            self.locations = amplify.decode_solution(q, result[0].values)

    def get_minimum_makespan(self):
        """compute the minimum makesapn for solutions (max min)

        Returns
        - int
        """
        return max([ self.get_dist_table([s], lambda n: n in self.instance["goals"])[0]
                     for s in self.instance["starts"] ])

    def validate_locations(self):
        """check consistency

        Returns:
        - Boolean
        """
        if self.locations is None:
            return False
        # check starts
        starts_sorted = [ v for v in range(self.field["size"]) if int(self.locations[0][v]) == 1 ]
        if sorted(self.instance["starts"]) != starts_sorted:
            logger.warning(f"invalid solution w.r.t. starts with makespan={self.makespan}, continue solving")
            return False
        # check goals
        goals_sorted = [ v for v in range(self.field["size"]) if int(self.locations[-1][v]) == 1 ]
        if sorted(self.instance["goals"]) != goals_sorted:
            logger.warning(f"invalid solution w.r.t. goals with makespan={self.makespan}, continue solving")
            return False
        # check path body
        for t in range(1, len(self.locations)):
            agents = 0
            for v in range(len(self.locations[t])):
                if int(self.locations[t][v]) == 0:
                    continue
                # check continuity
                if any([ int(self.locations[t-1][u]) == 1 for u in (self.field["adj"][v] + [ v ]) ]):
                    agents += 1
                else:
                    logger.warning(
                        f"invalid solution w.r.t. continuity with makespan={self.makespan}, continue solving")
                    return False
            # check the number of agents
            if agents != self.instance["agents"]:
                logger.warning(
                    f"invalid solution w.r.t. #agents with makespan={self.makespan}, continue solving")
                return False
        return True

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
        if self.locations is None:
            return

        V = self.instance["agents"]
        self.solution = []
        self.solution.append(self.instance['starts'])
        for t in range(1, len(self.locations)):

            # use Hopcroft-Karp algorithm to make paths
            # c.f., https://github.com/spaghetti-source/algorithm/blob/master/graph/bipartite_matching_HK.cc

            # create a bipartite graph
            L = self.solution[t-1]  # list of indexes
            R = [ v for v, loc in enumerate(self.locations[t]) if int(loc) == 1 ]  # list of indexes
            adj = [ [] for _ in range(V*2) ]
            for i in range(V):
                for j in range(V):
                    # create edge
                    if L[i] == R[j] or R[j] in self.field["adj"][L[i]]:
                        adj[i].append(V+j)
                        adj[V+j].append(i)

            level = [ 0 ] * V
            mate = [ None ] * (V * 2)

            print(L)
            print(R)
            print(adj)

            # BFS
            def levelize():
                # setup OPEN list
                Q = queue.Queue()
                for u in range(V):
                    level[u] = -1
                    if mate[u] == None:
                        level[u] = 0
                        Q.put(u)
                # main loop
                while not Q.empty():
                    u = Q.get()
                    for w in adj[u]:
                        v = mate[w]
                        if v is None:
                            return True
                        if level[v] < 0:
                            level[v] = level[u] + 1
                            Q.put(v)
                return False

            # find an augumenting path
            def augment(u):
                for w in adj[u]:
                    v = mate[w]
                    if v is None or (level[v] > level[u] and augment(v)):
                        mate[u] = w
                        mate[w] = u
                        return True
                return False

            match = 0
            while levelize():
                for u in range(V):
                    if mate[u] is None and augment(u):
                        match += 1

            if match != V:
                logger.error("the locations are infeasible")
                print(mate[:V])
                sys.exit()

            # update solution
            self.solution.append([ R[mate[l]-V] for l in range(V) ])
