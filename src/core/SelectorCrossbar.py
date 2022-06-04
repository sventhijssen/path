from __future__ import annotations

import copy

from typing import Dict, List

from networkx import has_path, shortest_path
from z3 import Bool

from aux import config
from core.Crossbar import Crossbar
from aux.DotGenerator import DotGenerator
from aux.LatexGenerator import LatexGenerator
from core.Literal import Literal


class SelectorCrossbar(Crossbar):
    """
    Type of crossbar where literals are assigned to nanowires.
    """

    def merge(self) -> Crossbar:
        # TODO: Implement
        pass

    def get_matrix(self):
        return self.matrix

    def draw_graph(self, benchmark_name: str):
        pass

    def write_xbar(self):
        content = ".xbar {} 1T1M".format(self.name)
        content += "\r\n"
        content += ".r {}".format(self.rows)
        content += "\r\n"
        content += ".c {}".format(self.columns)
        content += "\r\n"
        content += ".l {}".format(self.layers)
        content += "\r\n"
        content += ".input {}".format(" ".join(self.get_input_variables()))
        content += "\r\n"
        content += ".output {}".format(" ".join(self.get_output_variables()))
        content += "\r\n"
        for (input_variable, (layer, index)) in self.input_nanowires.items():
            content += ".i {} {} {}".format(input_variable, layer, index)
            content += "\r\n"
        for (output_variable, (layer, index)) in self.output_nanowires.items():
            content += ".o {} {} {}".format(output_variable, layer, index)
            content += "\r\n"

        for i in range(len(self.literals)):
            literal = self.literals[i]
            content += ".s {} {} {}".format(1, i, literal)
            content += "\r\n"
        # TODO: Fix functions
        # content += ".f {}".format(self.functions)
        # content += "\r\n"
        # content += ".s {}".format(self.literals)
        # content += ".f {}".format(", ".join(self.functions))
        # content += "\r\n"
        # content += ".s {}".format(", ".join(self.literals))
        for r in range(self.rows):
            for c in range(self.columns):
                literal = self.get_memristor(r, c).literal
                if c < self.columns - 1:
                    content += "{}\t".format(literal)
                else:
                    content += "{}\r\n".format(literal)
        return content

    def __init__(self, rows: int, columns: int, layers: int = 1):
        super().__init__(rows, columns, layers)
        self.functions = []  # Nodes in BDD
        self.literals = []  # Edges in BDD

    def get_functions(self):
        functions = []
        for (node, _) in self.functions:
            functions.append(node)
        return functions

    def __copy__(self):
        crossbar = SelectorCrossbar(self.rows, self.columns)
        for r in range(self.rows):
            for c in range(self.columns):
                crossbar.set_memristor(r, c, self.get_memristor(r, c).literal)
        crossbar.input_variables = self.input_variables.copy()
        crossbar.input_nanowires = self.input_nanowires.copy()
        crossbar.output_nanowires = self.output_nanowires.copy()
        return crossbar

    def get_z3(self) -> Bool:
        pass

    def instantiate(self, instance: Dict[str, bool]) -> SelectorCrossbar:
        crossbar = copy.deepcopy(self)

        for c in range(len(self.literals)):
            literal = self.literals[c]
            if literal == Literal("False", False):
                for r in range(crossbar.rows):
                    crossbar.set_memristor(r, c, Literal("False", False))
            elif literal == Literal("True", True):
                continue
            else:
                if not instance[literal.atom] and literal.positive:
                    for r in range(crossbar.rows):
                        crossbar.set_memristor(r, c, Literal("False", False))
                elif instance[literal.atom] and not literal.positive:
                    for r in range(crossbar.rows):
                        crossbar.set_memristor(r, c, Literal("False", False))
        return crossbar

    def eval(self, instance: Dict[str, bool], input_function: str = "1") -> Dict[str, bool]:
        crossbar_instance = self.instantiate(instance)
        graph = crossbar_instance.graph().copy()
        not_stuck_on_edges = [(u, v) for u, v, d in graph.edges(data=True) if
                              not (d['atom'] == 'True' and d['positive'])]
        graph.remove_edges_from(not_stuck_on_edges)

        evaluation = dict()
        for (output_variable, (output_layer, output_nanowire)) in self.output_nanowires.items():
            source = "L{}_{}".format(output_layer, output_nanowire)
            input_layer, input_nanowire = crossbar_instance.get_input_nanowire(input_function)
            sink = "L{}_{}".format(input_layer, input_nanowire)

            is_true = has_path(graph, source, sink)
            evaluation[output_variable] = is_true

            if config.trace:
                if is_true:
                    path = shortest_path(graph, source=source, target=sink, weight=None, method='dijkstra')
                    print(path)
                    self.draw_matrix("trace", path)

        return evaluation

    # def draw_matrix(self, benchmark_name: str):
    #     content = ''
    #     content += '\\documentclass{article}\n'
    #     content += '\\usepackage{tikz,amsmath,siunitx}\n'
    #     content += '\\usetikzlibrary{arrows,snakes,backgrounds,patterns,matrix,shapes,fit,calc,shadows,plotmarks}\n'
    #     content += '\\usepackage[graphics,tightpage,active]{preview}\n'
    #     content += '\\PreviewEnvironment{tikzpicture}\n'
    #     content += '\\PreviewEnvironment{equation}\n'
    #     content += '\\PreviewEnvironment{equation*}\n'
    #     content += '\\newlength{\imagewidth}\n'
    #     content += '\\newlength{\imagescale}\n'
    #     content += '\\pagestyle{empty}\n'
    #     content += '\\thispagestyle{empty}\n'
    #     content += '\\begin{document}\n'
    #     content += '\\begin{tikzpicture}[OFF/.style={circle, draw, fill = gray!40, minimum size=8, inner sep=0pt, ' \
    #                'text width=6mm, align=center},ON/.style={circle, draw, fill = green!40, minimum size=8, ' \
    #                'inner sep=0pt, text width=6mm, align=center},VAR/.style={circle, draw, fill = blue!40, ' \
    #                'minimum size=8, inner sep=0pt, text width=6mm, align=center},BARE/.style={circle, draw=none, ' \
    #                'minimum size=8, inner sep=0pt, text width=6mm, align=center}]\n '
    #
    #     for c in range(self.columns):
    #         for r in range(self.rows):
    #             if self.get_memristor(r, c).literal.atom == 'False':
    #                 v = '$\\scriptscriptstyle 0$'
    #                 s = 'OFF'
    #             elif self.get_memristor(r, c).literal.atom == 'True':
    #                 v = '$\\scriptscriptstyle 1$'
    #                 s = 'ON'
    #             else:
    #                 if not self.get_memristor(r, c).literal.positive:
    #                     v = '$\\scriptscriptstyle \\neg ' + self.get_memristor(r, c).literal.atom + '$'
    #                 else:
    #                     v = '$\\scriptscriptstyle ' + self.get_memristor(r, c).literal.atom + '$'
    #                 s = 'VAR'
    #             content += '\\node[%s](n%d_%d) at (0.8*%d, 0.8*%d) {%s};\n' % (
    #                 s, c + 1, self.rows - r, c + 1, self.rows - r, v)
    #
    #     for c in range(self.columns - 1):
    #         for r in range(self.rows):
    #             content += '\\draw (n%d_%d) -- (n%d_%d);\n' % (c + 1, r + 1, c + 2, r + 1)
    #
    #     for c in range(self.columns):
    #         for r in range(self.rows - 1):
    #             content += '\\draw (n%d_%d) -- (n%d_%d);\n' % (c + 1, r + 1, c + 1, r + 2)
    #
    #     # Literals
    #     for c in range(len(self.literals)):
    #         v = '$\\scriptscriptstyle {}$'.format(str(self.literals[c]).replace("\\+", "\sim "))
    #         content += '\\node[BARE](n%d_%d) at (0.8*%d, 0.8*%d) {%s};\n' % (c + 1, 0, c + 1, 0, v)
    #
    #     # Functions
    #     for r in range(len(self.functions)):
    #         v = '$\\scriptscriptstyle {}$'.format(self.functions[r])
    #         content += '\\node[BARE](n%d_%d) at (0.8*%d, 0.8*%d) {%s};\n' % (0, self.rows - r, 0, self.rows - r, v)
    #         # content += '\\draw (n%d_%d) -- (n%d_%d);\n' % (0, 0, 1, 0)
    #
    #     # # Input
    #     # v = '$\\scriptscriptstyle Vin$'
    #     # content += '\\node[BARE](n%d_%d) at (0.8*%d, 0.8*%d) {%s};\n' % (0, 0, 0, 0, v)
    #     # content += '\\draw (n%d_%d) -- (n%d_%d);\n' % (0, 0, 1, 0)
    #
    #     # Outputs
    #     for (o, r) in self.output_nanowires.items():
    #         v = '$\\scriptscriptstyle ' + o + '$'
    #         content += '\\node[BARE](n%d_%d) at (0.8*%d, 0.8*%d) {%s};\n' % (
    #             self.columns + 1, self.rows - r, self.columns + 1, self.rows - r, v)
    #         content += '\\draw (n%d_%d) -- (n%d_%d);\n' % (self.columns, self.rows - r, self.columns + 1, self.rows - r)
    #
    #     content += '\\end{tikzpicture}\n'
    #     content += '\\end{document}\n'
    #
    #     LatexGenerator.generate(benchmark_name, content)

    def draw_dot(self, benchmark_name: str):
        # We draw a separate crossbar matrix for each layer of memristors.
        # Grid after https://graphviz.org/Gallery/undirected/grid.html
        # Node distance after https://newbedev.com/how-to-manage-distance-between-nodes-in-graphviz
        for layer in range(self.get_memristor_layers()):
            content = ''
            content += 'graph {} {{\n'.format(benchmark_name)
            content += '\tgraph [nodesep="0.2", ranksep="0.2"];\n'
            content += '\tcharset="UTF-8"\n'
            content += '\tratio=fill\n'
            content += '\tsplines=spline\n'
            content += '\toverlap=scale\n'
            content += '\tnode [shape=circle, fixedsize=true, width=0.4, fontsize=12];\n'
            content += '\n'

            content += '\n\t// Memristors\n'
            for c in range(self.columns):
                for r in range(self.rows):
                    if self.get_memristor(r, c, layer).literal.atom == 'False':
                        v = '0'
                        style = 'color="#000000", fillcolor="#eeeeee", style="filled,solid"'
                    elif self.get_memristor(r, c, layer).literal.atom == 'True':
                        v = '1'
                        style = 'color="#000000", fillcolor="#cadfb8", style="filled,solid"'
                    else:
                        if not self.get_memristor(r, c, layer).literal.positive:
                            v = '¬' + self.get_memristor(r, c, layer).literal.atom
                        else:
                            v = self.get_memristor(r, c, layer).literal.atom
                        style = 'color="#000000", fillcolor="#b4c7e7", style="filled,solid"'
                    content += '\tm{}{} [label="{}" {}]\n'.format(r + 1, c + 1, v, style)

            content += '\n\t// Functions (left y-axis)\n'
            # Functions
            for r in range(len(self.functions)):
                input_rows = list(map(lambda i: i[1], self.get_input_nanowires().values()))
                style = 'color="#ffffff", fillcolor="#ffffff", style="filled,solid"'
                if r not in input_rows:
                    v = '{}'.format(self.functions[r][0])
                    content += '\tm{}{} [label="{}" {}]\n'.format(r + 1, 0, v, style)
                else:
                    v = ''
                    for (input_function, (layer, row)) in self.get_input_nanowires().items():
                        if r == row:
                            v = 'Vin<SUB>{}</SUB>'.format(input_function)
                    content += '\tm{}{} [label=<{}> {}]\n'.format(r + 1, 0, v, style)

            content += '\n\t// Outputs (right y-axis)\n'
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
                        v = os[i]
                        style = 'color="#ffffff", fillcolor="#ffffff", style="filled,solid"'
                        content += '\tm{}{} [label="{}" {}];\n'.format(r + 1, self.columns + 1, v, style)

            content += '\n\t// Crossbar\n'
            # Important: The description of the grid is transposed when being rendered -> rows and columns are switched
            for r in range(self.rows):
                input_rows = list(map(lambda i: i[1], self.get_input_nanowires().values()))
                content += '\trank=same {\n'
                for c in range(self.columns):
                    if r not in input_rows and c == 0:
                        content += '\t\tm{}{} -- m{}{} [style=invis];\n'.format(r + 1, c, r + 1, c + 1)
                    else:
                        content += '\t\tm{}{} -- m{}{};\n'.format(r + 1, c, r + 1, c + 1)

                # TODO: Change layer
                if (0, r) in output_variables:
                    content += '\t\tm{}{} -- m{}{};\n'.format(r + 1, self.columns, r + 1, self.columns + 1)
                content += '\t}\n'

            for c in range(self.columns):
                content += '\t' + ' -- '.join(["m{}{}".format(r + 1, c + 1) for r in range(self.rows)]) + '\n'

            content += '\n\t// Literals (bottom x-axis)\n'
            # content += '\tedge [style=invis];\n'
            # Literals
            for c in range(len(self.literals)):
                v = '{}'.format(str(self.literals[c]).replace("\\+", "¬"))
                style = 'color="#ffffff", fillcolor="#ffffff", style="filled,solid"'
                content += '\tm{}{} [label="{}" {}];\n'.format(self.rows + 1, c + 1, v, style)
                content += '\tm{}{} -- m{}{};\n'.format(self.rows, c + 1, self.rows + 1, c + 1)
            content += '\trank=same {' + ' '.join(["m{}{}".format(self.rows + 1, c + 1) for c in range(self.columns)]) + '}\n'

            # # Outputs
            # output_variables = dict()
            # for (o, (l, r)) in self.output_nanowires.items():
            #     if (l, r) in output_variables:
            #         output_variables[(l, r)].append(o)
            #     else:
            #         output_variables[(l, r)] = [o]
            # for ((l, r), os) in output_variables.items():
            #     if layer == l:
            #         for i in range(len(os)):
            #             v = os[i]
            #             style = 'color="#ffffff", fillcolor="#ffffff", style="filled,solid"'
            #             content += '\t m{}{} [label="{}" {}];\n'.format(r, self.columns + 2, v, style)
            #         content += '\t m{}{} -- m{}{};\n'.format(r, self.columns + 1, r, self.columns + 2)
                    # content += '\\draw (n%d_%d) -- (n%d_%d);\n' % (self.columns, self.rows - r, self.columns + 1, self.rows - r)

            content += '}'

            DotGenerator.generate(benchmark_name + "_" + str(layer), content)

            return content

    def draw_matrix(self, benchmark_name: str, trace: List[str] = None):
        path = []

        if trace is not None:
            for i in range(0, len(trace) -1):
                current_graph_node = trace[i]
                next_graph_node = trace[i + 1]

                current_graph_node_layer_str, current_graph_node_index_str = current_graph_node.split("_")
                current_graph_node_layer = int(current_graph_node_layer_str[1:])
                current_graph_node_index = int(current_graph_node_index_str)

                next_graph_node_layer_str, next_graph_node_index_str = next_graph_node.split("_")
                next_graph_node_layer = int(next_graph_node_layer_str[1:])
                next_graph_node_index = int(next_graph_node_index_str)

                if current_graph_node_layer % 2 == 0:
                    matrix_node = (current_graph_node_index, next_graph_node_index)
                else:
                    matrix_node = (next_graph_node_index, current_graph_node_index)
                path.append(matrix_node)
        print(path)

        """
        TODO: Remove benchmark_name for future use.
        Draws a matrix representation of this memristor crossbar in LateX for each layer of memristors in this
        memristor crossbar.
        :param benchmark_name: The given name for the benchmark.
        :param trace:
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
            content += '\\begin{tikzpicture}[STUCK/.style={circle, fill = red!40, minimum size=8, inner sep=0pt, ' \
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

                    if (r, c) in path:
                        t = "draw=red, line width=1.2pt"
                    else:
                        t = "draw=black"

                    content += '\\node[%s, %s](n%d_%d) at (0.8*%d, 0.8*%d) {%s};\n' % (
                        s, t, c + 1, self.rows - r, c + 1, self.rows - r, v)

            for c in range(self.columns - 1):
                for r in range(self.rows):
                    content += '\\draw (n%d_%d) -- (n%d_%d);\n' % (c + 1, r + 1, c + 2, r + 1)

            for c in range(self.columns):
                for r in range(self.rows - 1):
                    content += '\\draw (n%d_%d) -- (n%d_%d);\n' % (c + 1, r + 1, c + 1, r + 2)

            # Literals
            for c in range(len(self.literals)):
                v = '$\\scriptscriptstyle {}$'.format(str(self.literals[c]).replace("\\+", "\\neg "))
                content += '\\node[BARE](n%d_%d) at (0.8*%d, 0.8*%d) {%s};\n' % (c + 1, 0, c + 1, 0, v)

            # Functions
            for r in range(len(self.functions)):
                input_rows = list(map(lambda i: i[1], self.get_input_nanowires().values()))
                if r not in input_rows:
                    v = '$\\scriptscriptstyle {}$'.format(self.functions[r])
                    content += '\\node[BARE](n%d_%d) at (0.8*%d, 0.8*%d) {%s};\n' % (0, self.rows - r, 0, self.rows - r, v)
                # content += '\\draw (n%d_%d) -- (n%d_%d);\n' % (0, 0, 1, 0)

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
