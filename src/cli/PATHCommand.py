from networkx import MultiDiGraph

from aux import config
from core.MemristorCrossbarTopology import MemristorCrossbarTopology
from synth.PATH import PATH
from cli.Command import Command


class PATHCommand(Command):

    def __init__(self, args: list):
        super(PATHCommand).__init__()

    def execute(self):
        context = config.context_manager.get_context()
        graph_topology = context.boolean_function
        context.crossbars = []

        boolean_function = context.boolean_function

        input_variables = boolean_function.get_input_variables()
        output_variables = boolean_function.get_output_variables()

        graph_to_xbar = dict()
        topology = MultiDiGraph()
        for graph in graph_topology.get_graphs():
            path = PATH()
            crossbar = path.map(graph)
            topology.add_node(crossbar)
            context.crossbars.append(crossbar)
            graph_to_xbar[graph] = crossbar

        interconnections = []
        # Place all edges between the crossbars
        for (g1, g2, data) in graph_topology.graph.edges(data=True):
            x1 = graph_to_xbar.get(g1)
            x2 = graph_to_xbar.get(g2)
            node = data["node"]
            r1 = x1.get_functions().index(node)
            r2 = x2.get_functions().index(node)
            topology.add_edge(x1, x2)
            interconnections.append(((x1, r1), (x2, r2)))

        crossbar_topology = MemristorCrossbarTopology(topology, interconnections)
        crossbar_topology.input_variables = input_variables
        crossbar_topology.output_variables = output_variables
        config.context_manager.add_context("", crossbar_topology)

        return False
