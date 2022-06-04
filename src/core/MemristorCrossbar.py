from __future__ import annotations

import copy
import numpy as np
from typing import Dict, List

from networkx import has_path, connected_components
from z3 import Bool

from core.Crossbar import Crossbar
from aux.DotGenerator import DotGenerator
from aux.LatexGenerator import LatexGenerator
from core.Literal import Literal


class MemristorCrossbar(Crossbar):
    """
    Type of crossbar where literals are assigned to memristors.
    """

    def __init__(self, rows: int, columns: int, layers: int = 1, default_literal=Literal("False", False)):
        """
        Constructs a memristor crossbar of dimensions (number of memristors) x by y.
        The optional dimension z indicates the number of layers of memristors.
        By default, the number of layers is 1.
        A memristor is defined by a triple (r, c, l) where r is the index of the nanowire below the memristor,
        c is the index of the nanowire above the memristor, and l is the layer of the memristor.
        A nanowire is defined by a tuple (i, l) where i is the index in a series of parallel nanowires at layer i.
        :param rows: The number of memristors along the input and output nanowires.
        :param columns: The number of memristors orthogonal to the input and output nanowires.
        :param layers: The number of layers of memristors.
        """
        super(MemristorCrossbar, self).__init__(rows, columns, layers, default_literal)
        self.input_rows = None

    def merge(self) -> Crossbar:
        # TODO: Implement
        pass

    def __copy__(self):
        crossbar = MemristorCrossbar(self.rows, self.columns, self.layers)
        crossbar.matrix = copy.deepcopy(self.matrix)
        # for layer in range(self.layers):
        #     for r in range(self.rows):
        #         for c in range(self.columns):
        #             memristor = self.get_memristor(r, c)
        #             stuck_at_fault = memristor.stuck_at_fault
        #             permanent = memristor.permanent
        #             crossbar.set_memristor(r, c, self.get_memristor(r, c).literal, layer, stuck_at_fault=stuck_at_fault,
        #                                    permanent=permanent)
        crossbar.input_nanowires = self.input_nanowires
        crossbar.input_variables = self.input_variables.copy()
        crossbar.output_nanowires = self.output_nanowires.copy()
        return crossbar

    # def __eq__(self, other):
    #     if not isinstance(other, MemristorCrossbar):
    #         return False
    #     dgt = DynamicGraphTree(other)
    #     benchmark = Benchmark('', self.input_variables, self.output_variables, self.z3())
    #     return dgt.is_equivalent(benchmark)

    def get_graph(self):
        return self.graph()

    def get_matrix(self):
        return self.matrix

    def get_lits(self):
        literals = set()
        for r in range(self.rows):
            for c in range(self.columns):
                if self.get_memristor(r, c).literal != Literal('True', True) and self.get_memristor(r, c).literal != Literal('False',
                                                                                                               False):
                    literals.add(self.get_memristor(r, c).literal)
        return literals

    def get_vars(self):
        variables = set()
        for r in range(self.rows):
            for c in range(self.columns):
                if self.get_memristor(r, c).literal != Literal('True', True) and self.get_memristor(r, c).literal != Literal('False',
                                                                                                               False):
                    variables.add(self.get_memristor(r, c).literal.atom)
        return variables

    def get_nr_variables(self):
        count = 0
        for r in range(self.rows):
            for c in range(self.columns):
                if self.get_memristor(r, c).literal != Literal('True', True) and self.get_memristor(r, c).literal != Literal('False',
                                                                                                               False):
                    count += 1
        return count

    def instantiate(self, instance: dict) -> MemristorCrossbar:
        for layer in range(self.layers):
            for r in range(self.rows):
                for c in range(self.columns):
                    memristor = self.get_memristor(r, c, layer)
                    literal = memristor.literal
                    variable_name = literal.atom
                    positive = literal.positive
                    if variable_name != "True" and variable_name != "False":
                        if not memristor.stuck_at_fault:
                            if positive:
                                if instance[variable_name]:
                                    literal = Literal('True', True)
                                else:
                                    literal = Literal('False', False)
                            else:
                                if instance[variable_name]:
                                    literal = Literal('False', False)
                                else:
                                    literal = Literal('True', True)
                            self.set_memristor(r, c, literal, layer=layer)
        return self

    def write_xbar(self) -> str:
        pass

    def eval(self, instance: Dict[str, bool], input_function: str = "1") -> Dict[str, bool]:
        # For all input nanowires different from a different input function than the given input function,
        # we set the literals False to avoid any loops through these nanowires.
        for (other_input_function, (layer, input_nanowire)) in self.get_input_nanowires().items():
            if input_function != other_input_function:
                for c in range(self.columns):
                    self.set_memristor(input_nanowire, c, Literal("False", False), layer=layer)

        crossbar_copy = self.__copy__()
        crossbar_instance = crossbar_copy.instantiate(instance)
        graph = crossbar_instance.graph()
        true_edges = [(u, v) for u, v, d in graph.edges(data=True) if
                              not (d['atom'] == 'True' and d['positive'])]
        graph.remove_edges_from(true_edges)

        evaluation = dict()
        for (output_variable, (output_layer, output_nanowire)) in crossbar_instance.get_output_nanowires().items():
            source = "L{}_{}".format(output_layer, output_nanowire)
            input_layer, input_nanowire = crossbar_instance.get_input_nanowire(input_function)
            sink = "L{}_{}".format(input_layer, input_nanowire)
            evaluation[output_variable] = has_path(graph, source, sink)

        return evaluation

    def draw_graph(self, benchmark_name: str):
        content = ''
        content += 'graph{\n'

        graph = self.graph()
        false_edges = [(u, v) for u, v, d in graph.edges(data=True) if
                       d['atom'] == 'False' and not d['positive']]
        graph.remove_edges_from(false_edges)

        for v in graph.nodes:
            node_attributes = v[1:]
            (layer, index) = node_attributes.split("_")
            content += '{} [layer="{}"]\n'.format(v, layer)

        for (u, v, d) in graph.edges(data=True):
            if d["positive"]:
                if d["atom"] == "True":
                    literal = "1"
                else:
                    literal = d["atom"]
            else:
                literal = "~" + d["atom"]
            content += '{} -- {} [label="{}"]\n'.format(u, v, literal)

        content += '}\n'

        DotGenerator.generate(benchmark_name, content)

    def draw_matrix(self, benchmark_name: str):
        """
        TODO: Remove benchmark_name for future use.
        Draws a matrix representation of this memristor crossbar in LateX for each layer of memristors in this
        memristor crossbar.
        :param benchmark_name: The given name for the benchmark.
        :return:
        """
        # We draw a separate crossbar matrix for each layer of memristors.
        for layer in range(self.get_memristor_layers()):
            content = ''
            content += '\\documentclass{article}\n'
            content += '\\usepackage{tikz,amsmath,siunitx}\n'
            content += '\\usetikzlibrary{arrows,snakes,backgrounds,patterns,matrix,shapes,fit,calc,shadows,plotmarks}\n'
            content += '\\usepackage[graphics,tightpage,active]{preview}\n'
            content += '\\PreviewEnvironment{tikzpicture}\n'
            content += '\\PreviewEnvironment{equation}\n'
            content += '\\PreviewEnvironment{equation*}\n'
            content += '\\newlength{\imagewidth}\n'
            content += '\\newlength{\imagescale}\n'
            content += '\\pagestyle{empty}\n'
            content += '\\thispagestyle{empty}\n'
            content += '\\begin{document}\n'
            content += '\\begin{tikzpicture}[STUCK/.style={circle, draw, fill = red!40, minimum size=8, inner sep=0pt, ' \
                       'text width=6mm, align=center},OFF/.style={circle, draw, fill = gray!40, minimum size=8, inner sep=0pt, ' \
                       'text width=6mm, align=center},ON/.style={circle, draw, fill = green!40, minimum size=8, ' \
                       'inner sep=0pt, text width=6mm, align=center},VAR/.style={circle, draw, fill = blue!40, ' \
                       'minimum size=8, inner sep=0pt, text width=6mm, align=center},BARE/.style={circle, draw=none, ' \
                       'minimum size=8, inner sep=0pt, text width=6mm, align=center}]\n'

            content += '\\textbf{Layer ' + str(layer) + '}\n'
            for c in range(self.columns):
                for r in range(self.rows):
                    if self.get_memristor(r, c, layer).literal.atom == 'False':
                        v = '$\\scriptscriptstyle 0$'
                        s = 'OFF'
                    elif self.get_memristor(r, c, layer).literal.atom == 'True':
                        v = '$\\scriptscriptstyle 1$'
                        s = 'ON'
                    else:
                        if not self.get_memristor(r, c, layer).literal.positive:
                            v = '$\\scriptscriptstyle \\neg ' + self.get_memristor(r, c, layer).literal.atom + '$'
                        else:
                            v = '$\\scriptscriptstyle ' + self.get_memristor(r, c, layer).literal.atom + '$'
                        s = 'VAR'
                    if self.get_memristor(r, c, layer).stuck_at_fault:
                        s = 'STUCK'
                    content += '\\node[%s](n%d_%d) at (0.8*%d, 0.8*%d) {%s};\n' % (
                        s, c + 1, self.rows - r, c + 1, self.rows - r, v)

            for c in range(self.columns - 1):
                for r in range(self.rows):
                    content += '\\draw (n%d_%d) -- (n%d_%d);\n' % (c + 1, r + 1, c + 2, r + 1)

            for c in range(self.columns):
                for r in range(self.rows - 1):
                    content += '\\draw (n%d_%d) -- (n%d_%d);\n' % (c + 1, r + 1, c + 1, r + 2)

            # if self.layers == 1:
            #
            #     # Inputs
            #     for (i, r) in self.input_nanowires.items():
            #         v = '$\\scriptscriptstyle Vin_{}$'.format(i)
            #         content += '\\node[BARE](n%d_%d) at (0.8*%d, 0.8*%d) {%s};\n' % (0, self.rows - r, 0, self.rows - r, v)
            #         content += '\\draw (n%d_%d) -- (n%d_%d);\n' % (0, self.rows - r, 1, self.rows - r)
            #
            #     # # Outputs
            #     for (o, r) in self.output_variables.items():
            #         v = '$\\scriptscriptstyle ' + o + '$'
            #         content += '\\node[BARE](n%d_%d) at (0.8*%d, 0.8*%d) {%s};\n' % (
            #             self.columns + 1, self.rows - r, self.columns + 1, self.rows - r, v)
            #         content += '\\draw (n%d_%d) -- (n%d_%d);\n' % (self.columns, self.rows - r, self.columns + 1, self.rows - r)
            # else:
            # TODO: Uncomment for 3D
            # Inputs
            for (i, (l, r)) in self.get_input_nanowires().items():
                if layer == l:
                    v = '$\\scriptscriptstyle Vin_{}$'.format(i)
                    content += '\\node[BARE](n%d_%d) at (0.8*%d, 0.8*%d) {%s};\n' % (0, self.rows - r, 0, self.rows - r, v)
                    content += '\\draw (n%d_%d) -- (n%d_%d);\n' % (0, self.rows - r, 1, self.rows - r)

            # Outputs
            output_variables = dict()
            for (o, (l, r)) in self.output_nanowires.items():
                if (l, r) in output_variables:
                    output_variables[(l, r)].append(o)
                else:
                    output_variables[(l, r)] = [o]
            for ((l, r), os) in output_variables.items():
                if layer == l:
                    for i in range(len(os)):
                        o = os[i]
                        v = '$\\scriptscriptstyle ' + o + '$'
                        content += '\\node[BARE](n%d_%d) at (0.8*%d, 0.8*%d) {%s};\n' % (
                            self.columns + 1 + i, self.rows - r, self.columns + 1 + i, self.rows - r, v)
                    content += '\\draw (n%d_%d) -- (n%d_%d);\n' % (self.columns, self.rows - r, self.columns + 1, self.rows - r)

            content += '\\end{tikzpicture}\n'
            content += '\\end{document}\n'

            LatexGenerator.generate(benchmark_name + "_" + str(layer), content)
