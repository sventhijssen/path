from networkx import DiGraph

from synth.PATH import PATH


class CrossbarPartitioning:

    def __init__(self, topological_graph: DiGraph, D: int):
        self.topological_graph = topological_graph
        self.D = D
        self.crossbars = []
        self.interconnections = []
        self._update_interconnections()

    def _update_interconnections(self):
        i = 0
        for g in self.topological_graph.nodes:
            path = PATH()
            raw_xbar = path.map(g)
            # xbar = Map(raw_xbar, SelectorCrossbar(self.D, self.D))
            # self.crossbars.append(xbar)

        for (g1, g2) in self.topological_graph.edges:
            pass

