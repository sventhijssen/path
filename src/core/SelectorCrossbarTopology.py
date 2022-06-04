import re
from typing import Dict

from networkx import DiGraph, topological_sort

from core.CrossbarTopology import CrossbarTopology
from aux.DotGenerator import DotGenerator
from core.Literal import Literal


class SelectorCrossbarTopology(CrossbarTopology):

    def __init__(self, topology: DiGraph, interconnections):
        """
        A crossbar topology is a directed acyclic graph of crossbars.
        Each node in the graph is a crossbar, and each edge between the nodes is a connection between rows.
        :param topology:    A directed acyclic graph of crossbars.
        """
        super().__init__()
        self.topology = topology
        self.inter_connections = interconnections

    def write_xbar(self) -> str:
        content = ""
        for crossbar in self.topology.nodes:
            content += crossbar.write_xbar()
        for ((x1, (l1, i1)), (x2, (l2, i2))) in self.inter_connections:
            content += ".ic {} {} {} {} {} {}".format(x1.name, l1, i1, x2.name, l2, i2)
            content += "\r\n"
        return content

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

        for ((x1, (l1, i1)), (x2, (l2, i2))) in self.inter_connections:
            nr1 = xbar_to_nr[x1]
            nr2 = xbar_to_nr[x2]
            if l2 == 0:
                r1 = i1 + 1
                r2 = i2 + 1
                c1 = x1.columns
                c2 = 1
            else:
                r1 = i1 + 1
                r2 = x2.rows + 1
                c1 = x1.columns
                c2 = i2 + 1

            content += '\ts{}m{}{} -- s{}m{}{} [style = dashed, penwidth = 1, color="#000000"];\n'.format(nr1, r1, c1, nr2, r2, c2)

        content += '}'

        DotGenerator.generate(name, content)

    def draw_matrix(self, name):
        i = 0
        for node in self.topology.nodes:
            node.draw_matrix("{}_{}".format(name, i))
            i += 1

    def eval(self, instance: Dict[str, bool], input_function: str = "1") -> Dict[str, bool]:
        """
        Evaluates a crossbar topology for a given instance.
        :param instance:
        :param input_function:
        :return:
        """

        # An interconnection is a tuple of a crossbar x and a tuple of a layer l and an index i: (x, (l, i)).
        # In 2D crossbars, layer l=0 is a row, and layer l=1 is a column.
        connections = dict()
        i = 0
        for ((x1, (l1, i1)), (x2, (l2, i2))) in self.inter_connections:
            x1.output_nanowires["inter_{}".format(i)] = (l1, i1)
            x2.input_nanowires["inter_{}".format(i)] = (l2, i2)
            connections[(x1, "inter_{}".format(i))] = x2
            i += 1

        evaluations = {"1": True}
        for crossbar in topological_sort(self.topology):

            # Set literals if there are any input functions to the selector lines
            for (input_function, (layer, index)) in crossbar.input_nanowires.items():
                if layer == 1:
                    input_value = evaluations.get(input_function)
                    if input_value:
                        crossbar.literals[index] = Literal("True", True)
                    else:
                        crossbar.literals[index] = Literal("False", False)

            for (input_function, (layer, index)) in crossbar.input_nanowires.items():
                if layer == 0:
                    input_value = evaluations.get(input_function)
                    if input_value:
                        evaluation = crossbar.eval(instance, input_function)

                        for (output_function, output_value) in evaluation.items():
                            # Do not update output function to False if already True
                            if output_function not in evaluations:
                                evaluations[output_function] = output_value
                            else:
                                current_output_value = evaluations.get(output_function)
                                if not current_output_value and output_value:
                                    evaluations[output_function] = output_value
                    else:
                        for output_function in crossbar.get_output_variables():
                            if output_function not in evaluations:
                                evaluations[output_function] = False
                            else:
                                current_output_value = evaluations.get(output_function)
                                if not current_output_value:
                                    evaluations[output_function] = False

        evaluation = dict()
        for output_variable in self.output_variables:
            evaluation[output_variable] = evaluations.get(output_variable)

        return evaluation

