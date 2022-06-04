import time

from aux import config
from aux.MappingMethod import MappingMethod
from core.Literal import Literal
from core.SelectorCrossbar import SelectorCrossbar


class PATH(MappingMethod):

    def __init__(self):
        super(PATH, self).__init__()
        self.start_time = time.time()
        self.end_time = time.time()

    def map(self, graph):
        print("PATH started")
        print("Nodes: {}".format(len(graph.nodes)))
        print("Edges: {}".format(len(graph.edges)))
        # config.log.add("PATH version: ?\n")
        config.log.add("Nodes: {}\n".format(len(graph.nodes)))
        config.log.add("Edges: {}\n".format(len(graph.edges)))
        rows = len(graph.nodes)
        columns = len(graph.edges)
        self.crossbar = SelectorCrossbar(rows, columns)
        config.log.add("Rows: {}\n".format(rows))
        config.log.add("Columns: {}\n".format(columns))
        self.crossbar.literals = list(map(lambda x: Literal(x[2]['variable'], bool(x[2]['positive'])), graph.edges(data=True)))
        # self.crossbar.functions = list(map(lambda x: x[1]['variable'], graph.nodes(data=True)))
        self.crossbar.functions = list(graph.nodes(data=True))
        literals = list(graph.edges)
        functions = list(graph.nodes)

        node_output_variables = list(map(lambda x: (x[0], x[1]['output_variables']), filter(lambda x: x[1]['root'] == True, graph.nodes(data=True))))

        for (node, output_variables) in node_output_variables:
            row = functions.index(node)
            for output_variable in output_variables:
                self.crossbar.set_output_nanowire(output_variable, row)
            # self.crossbar.output_nanowires[output_variable] = row

        node_input_variables = list(map(lambda x: (x[0], x[1]['variable']), filter(lambda x: x[1]['terminal'] == True, graph.nodes(data=True))))
        for (node, input_variable) in node_input_variables:
            row = functions.index(node)
            self.crossbar.set_input_nanowire(input_variable, row)

        for (x, y) in graph.edges:
            r0 = functions.index(x)
            r1 = functions.index(y)
            c = literals.index((x, y))
            self.crossbar.set_memristor(r0, c, Literal("True", True))
            self.crossbar.set_memristor(r1, c, Literal("True", True))

        self.end_time = time.time()

        config.log.add('PATH time (s): {}\n'.format(self.end_time - self.start_time))

        print("PATH stopped")

        return self.crossbar

    def get_log(self) -> str:
        log = ''
        log += 'COMPACT time (s): {}\n'.format(self.end_time - self.start_time)
        return log
