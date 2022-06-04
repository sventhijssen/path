import re
from typing import Dict

from networkx import DiGraph, topological_sort

from aux import config
from core.CrossbarTopology import CrossbarTopology
from aux.DotGenerator import DotGenerator


class MemristorCrossbarTopology(CrossbarTopology):

    def __init__(self, topology: DiGraph, interconnections):
        """
        A crossbar topology is a directed acyclic graph of crossbars.
        Each node in the graph is a crossbar, and each edge between the nodes is a connection between rows.
        :param topology:    A directed acyclic graph of crossbars.
        """
        super().__init__()
        self.topology = topology
        self.inter_connections = interconnections

    def draw_dot(self, name):
        """
        https://hbfs.wordpress.com/2014/09/30/a-quick-primer-on-graphviz/
        :param name:
        :return:
        """

        xbar_to_nr = dict()

        content = ''

        i = 0
        content += 'graph {} {{\n'.format(name)
        content += '\trankdir=TB;\n'
        content += '\tcompound=true;\n'
        content += '\tgraph [nodesep="0.2", ranksep="0.2"];\n'
        content += '\tcharset="UTF-8";\n'
        content += '\tratio=fill;\n'
        content += '\tsplines=line;\n'
        content += '\toverlap=scale;\n'
        content += '\tnode [shape=circle, fixedsize=true, width=0.4, fontsize=12];\n'
        content += '\n'
        for node in self.topology.nodes:
            subgraph = node.draw_dot("{}_{}".format(name, i))
            xbar_to_nr[node] = i
            subgraph = re.sub(r'(m\d+)', r's{}\1'.format(i), subgraph)
            subgraph = subgraph.splitlines()
            subgraph = subgraph[1:-1]
            subgraph = "\n".join(subgraph)
            content += '\tsubgraph cluster{} {{\n'.format(i)
            content += '\t\tlabel="{}"\n'.format(i)
            content += subgraph
            content += '\t}\n\n'
            i += 1

        for ((x1, r1), (x2, r2)) in self.inter_connections:
            c1 = x1.columns
            c2 = 1
            nr1 = xbar_to_nr[x1]
            nr2 = xbar_to_nr[x2]
            content += '\ts{}m{}{} -- s{}m{}{} [style = dashed, penwidth = 1, color="#000000"];\n'.format(nr1, r1 + 1, c1, nr2, r2 + 1, c2)
        content += '}'

        DotGenerator.generate(name, content)

    def draw_matrix(self, name):
        i = 0
        for node in self.topology.nodes:
            node.draw_matrix("{}_{}".format(name, i))
            i += 1

    def write_xbar(self) -> str:
        content = ""
        for crossbar in self.topology.nodes:
            content += crossbar.write_xbar()
        return content

    def eval(self, instance: Dict[str, bool], input_function: str = "1") -> Dict[str, bool]:
        """
        Evaluates a crossbar topology for a given instance.
        :param instance:
        :param input_function:
        :return:
        """
        connections = dict()
        i = 0
        for ((x1, r1), (x2, r2)) in self.inter_connections:
            x1.output_nanowires["inter_{}".format(i)] = (0, r1)
            x2.input_nanowires["inter_{}".format(i)] = (0, r2)
            connections[(x1, "inter_{}".format(i))] = x2
            i += 1

        root = list(topological_sort(self.topology))[0]
        queue = [(root, input_function)]

        output_evaluations = set()

        while len(queue) != 0:
            crossbar, input_function = queue.pop()

            if config.trace:
                print(crossbar)

            evaluation = crossbar.eval(instance, input_function)
            for (output_function, value) in evaluation.items():
                if value:
                    if output_function.startswith("inter"):
                        next_crossbar = connections.get((crossbar, output_function))
                        queue.append((next_crossbar, output_function))
                    else:
                        output_evaluations.add(output_function)

        evaluation = dict()
        for output_variable in self.output_variables:
            if output_variable in output_evaluations:
                evaluation[output_variable] = True
            else:
                evaluation[output_variable] = False

        return evaluation

