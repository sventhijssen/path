from typing import List

from aux import config
from core.GraphTopology import GraphTopology
from aux.ILPGraphPartitioning import ILPGraphPartitioning
from cli.Command import Command


class BDDPartitionCommand(Command):

    def __init__(self, args: List[str]):
        """
        Command to partition a BDD.

        :param args: A list of required and optional arguments.

        partition DIMENSION [-a FLOAT] [-k NUM] [-t FLOAT]

        Required arguments:

        - The first argument is the maximum dimension of the crossbar.

        Optional arguments:

        -a  Alpha; value between [0,1]. By default 0.5.

        -k  Maximum number of crossbars.

        -t  Time limit in seconds.

        """
        super(Command).__init__()

        if len(args) < 2:
            raise Exception("Missing argument.")

        self.d = int(args[0])

        if "-a" in args:
            idx = args.index("-a")
            self.alpha = float(args[idx + 1])
        else:
            self.alpha = 0.5

        if "-k" in args:
            idx = args.index("-k")
            self.k = int(args[idx + 1])
        else:
            self.k = None

        if "-t" in args:
            idx = args.index("-t")
            config.time_limit_partition = float(args[idx + 1])
        else:
            config.time_limit_partition = None

    def execute(self):
        """
        Executes the partitioning on a BDD.
        The BDD is obtained from the current context.
        :return:
        """

        context = config.context_manager.get_context()

        boolean_function = context.boolean_function

        graph = boolean_function.get_graphs()[0]

        input_variables = boolean_function.get_input_variables()
        output_variables = boolean_function.get_output_variables()

        gp = ILPGraphPartitioning(graph, self.d, self.alpha, self.k)
        graphs = gp.partition()

        graph_topology = GraphTopology(input_variables, output_variables)
        for graph in graphs:
            graph_topology.add_graph(graph)

        # TODO: Fix
        config.context_manager.add_context("_partition", graph_topology)

        return False
