import re
import time
from datetime import datetime
from math import ceil

from networkx import Graph
from pulp import CPLEX_CMD, LpVariable, LpInteger, LpProblem, LpMinimize, lpSum, LpStatusInfeasible, LpStatus

from aux import config


class ILPGraphPartitioning:

    def __init__(self, graph: Graph, D: int, alpha: float = 0.5, K: float = None):
        self.graph = graph
        if K is None:
            self.K = int(ceil(1.2 * max(len(self.graph.nodes), len(self.graph.edges)) / D))
        else:
            self.K = K
        self.D = D
        self.alpha = alpha
        self.start_time = None
        self.end_time = None
        self.log = ""

    def get_log(self) -> str:
        return self.log

    def partition(self):
        print("Number of nodes: {}".format(len(self.graph.nodes)))
        print("Number of edges: {}".format(len(self.graph.edges)))
        print("Maximum number of crossbars: {}".format(self.K))
        config.log.add("Number of nodes: {}\n".format(len(self.graph.nodes)))
        config.log.add("Number of edges: {}\n".format(len(self.graph.edges)))
        config.log.add("Partition alpha: {}\n".format(self.alpha))
        config.log.add("Partition D: {}\n".format(self.D))
        config.log.add("Partition K: {}\n".format(self.K))

        self.start_time = time.time()

        print(datetime.now())

        solver = CPLEX_CMD(path=config.cplex_path, msg=False, keepFiles=config.keep_files, timeLimit=config.time_limit_partition,
                           logPath=str(config.root.joinpath("cplex.log")))

        # Variables
        v_vars = LpVariable.dicts("v", (self.graph.nodes, [i for i in range(self.K)]), 0, 1, LpInteger)
        e_vars = LpVariable.dicts("e", (self.graph.edges, [i for i in range(self.K)]), 0, 1, LpInteger)
        x_vars = LpVariable.dicts("x", range(self.K), 0, 1, LpInteger)

        I = LpVariable("I")
        N = LpVariable("N")
        S = LpVariable("S")  # Objective

        # MIP problem
        lpvc = LpProblem("VC", LpMinimize)

        # Objective
        lpvc += S
        lpvc += S == self.alpha * N + (1 - self.alpha) * I

        # An edge must be placed in at least one crossbar.
        for e in self.graph.edges:
            lpvc += lpSum(e_vars[e]) == 1

        # Given an edge e=(u,v).
        # When e is placed in crossbar k, then both u and v must be placed in crossbar k.
        # When u and v must be placed in crossbar k, then e must NOT necessarily be placed in k.
        for e in self.graph.edges:
            for k in range(self.K):
                lpvc += 2 * e_vars[e][k] <= v_vars[e[0]][k] + v_vars[e[1]][k]

        # The number of nodes in a crossbar k must be smaller than the dimension D
        for k in range(self.K):
            lpvc += lpSum([v_vars[v][k] for v in self.graph.nodes]) <= self.D
            lpvc += lpSum([e_vars[e][k] for e in self.graph.edges]) <= self.D

        # If the number of nodes in a crossbar k is zero, then crossbar k is not used.
        # Otherwise, the crossbar is used.
        # x = max(0, min(1, sum))
        # Definition of min and max are based on:
        # https://math.stackexchange.com/questions/2446606/linear-programming-set-a-variable-the-max-between-two-another-variables
        for v in self.graph.nodes:
            for k in range(self.K):
                lpvc += v_vars[v][k] <= x_vars[k]

        for k in range(self.K - 1):
            lpvc += x_vars[k] >= x_vars[k + 1]

        lpvc += lpSum(x_vars) == N
        lpvc += lpSum(v_vars) == I

        lpvc.solve(solver)

        if lpvc.status == LpStatusInfeasible:
            raise InfeasibleSolutionException("Infeasible solution.")

        self.end_time = time.time()

        config.log.add('Partition ILP time (s): {}\n'.format(self.end_time - self.start_time))

        N = int(round(N.varValue))
        I = int(round(I.varValue))

        print("Partition status: {}".format(LpStatus[lpvc.status]))
        print("Partition objective S: {}".format(S.varValue))
        print("N: {}".format(N))
        print("I: {}".format(I))

        config.log.add("Partition status: {}\n".format(LpStatus[lpvc.status]))
        config.log.add("Partition objective S: {}\n".format(S.varValue))
        config.log.add("N: {}\n".format(N))
        config.log.add("I: {}\n".format(I))
        config.log.add("Roots: {}\n".format(
            list(map(lambda v: v[0], filter(lambda x: x[1]['root'] == True, self.graph.nodes(data=True))))))
        config.log.add("Terminal: {}\n".format(
            list(map(lambda v: v[0], filter(lambda x: x[1]['terminal'] == True, self.graph.nodes(data=True))))))

        all_node_assignments = []
        all_edge_assignments = []
        for k in range(self.K):
            all_node_assignments.append([])
            all_edge_assignments.append([])

        for v in self.graph.nodes:
            for k in range(self.K):
                value = int(round(v_vars[v][k].varValue))
                if value == 1:
                    all_node_assignments[k].append(v)

        for e in self.graph.edges:
            for k in range(self.K):
                value = int(round(e_vars[e][k].varValue))
                if value == 1:
                    all_edge_assignments[k].append(e)

        node_assignments = list(filter(lambda l: l, all_node_assignments))
        edge_assignments = list(filter(lambda l: l, all_edge_assignments))

        nr_crossbars = max(len(node_assignments), len(node_assignments))

        labeling = (nr_crossbars, node_assignments, edge_assignments)

        config.log.add(self.get_log())

        gap = 0
        cplex_log_file_name = config.root.joinpath("cplex.log")
        if cplex_log_file_name.is_file():
            with open(str(cplex_log_file_name), 'r') as f:
                for line in f.readlines():
                    if "gap" in line:
                        gap = float(re.findall(r'(\d+\.\d+)\%', line)[0])
        config.log.add("Gap (%): {}\n".format(gap))

        graph_partitions = []
        for k in range(nr_crossbars):
            graph_partition = self.graph.copy(as_view=False)
            subgraph_nodes = set(node_assignments[k])
            subgraph_edges = set(edge_assignments[k])
            node_difference = set(self.graph.nodes) - subgraph_nodes
            edge_difference = set(self.graph.edges) - subgraph_edges
            graph_partition.remove_nodes_from(node_difference)
            graph_partition.remove_edges_from(edge_difference)
            graph_partitions.append(graph_partition)

            config.log.add("\tCrossbar: {}\n".format(k))
            config.log.add("\tRows: {}\n".format(len(graph_partition.nodes)))
            config.log.add("\tColumns: {}\n".format(len(graph_partition.edges)))
            config.log.add("\tNodes: {}\n".format(graph_partition.nodes))
            config.log.add("\tEdges: {}\n".format(graph_partition.edges))

        return graph_partitions
