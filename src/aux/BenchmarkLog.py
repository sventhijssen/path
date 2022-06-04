from aux import config
from core.Literal import Literal


class BenchmarkLog:

    def __init__(self):
        self.context = None
        # self.start_time = time()
        self.mapping_method = None
        self.content = ''
        # self.simulation_size = 0
        # self.min_true_signal = 0
        # self.max_false_signal = 0
        # self.avg_true_signal = 0
        # self.avg_false_signal = 0

    def write(self, file_name: str = None):
        if not file_name:
            file_name = self.context.benchmark.name + '_' + config.bdd + '_' + config.mapping_method + '_' + str(
                config.gamma) + '.txt'
        with open(file_name, 'w') as f:
            f.write('Benchmark: {}\n'.format(self.context.benchmark.name))
            f.write('BDD type: {}\n'.format(config.bdd))
            f.write('Mapping method: {}\n'.format(config.mapping_method))
            f.write('Gamma: {}\n'.format(config.gamma))
            f.write('Inputs: {}\n'.format(len(self.context.benchmark.input_variables)))
            f.write('Outputs: {}\n'.format(len(self.context.benchmark.output_variables)))
            f.write('Vertices: {}\n'.format(len(self.context.benchmark_graph.nodes)))
            f.write('Edges: {}\n'.format(len(self.context.benchmark_graph.edges)))
            f.write('Rows: {}\n'.format(self.context.crossbars.rows))
            f.write('Columns: {}\n'.format(self.context.crossbars.columns))
            f.write('Semiperimeter: {}\n'.format(self.context.crossbars.rows + self.context.crossbars.columns))
            area = self.context.crossbars.rows * self.context.crossbars.columns
            f.write('Area: {}\n'.format(area))
            # f.write('Duration (s): {}\n'.format(time() - self.start_time))
            nr_on = len(self.context.crossbars.find(Literal("True", True)))
            nr_off = len(self.context.crossbars.find(Literal("False", False)))
            nr_vars = area - nr_on - nr_off
            f.write('ON: {}\n'.format(nr_on))
            f.write('OFF: {}\n'.format(nr_off))
            f.write('Vars: {}\n'.format(nr_vars))
            # if config.bdd_parser is not None:
            #     f.write(config.bdd_parser.get_log())
            # if self.mapping_method is not None:
            #     f.write(self.mapping_method.get_log())
            f.write(self.content)

            # f.write('Simulation size: {}\n'.format(self.simulation_size))
            # f.write('Minimum true signal: {:.2E}\n'.format(self.min_true_signal))
            # f.write('Maximum false signal: {:.2E}\n'.format(self.max_false_signal))
            # f.write('Average true signal: {:.2E}\n'.format(self.avg_true_signal))
            # f.write('Average false signal: {:.2E}\n'.format(self.avg_false_signal))
            f.write('\n')
