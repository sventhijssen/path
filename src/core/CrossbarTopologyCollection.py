from typing import Dict, Set

from core.BooleanFunction import BooleanFunction
from core.CrossbarTopology import CrossbarTopology


class CrossbarTopologyCollection(BooleanFunction):

    def __init__(self):
        super().__init__()
        self.input_variables = set()
        self.output_variable_to_topology = dict()

    def get_input_variables(self) -> Set[str]:
        return self.input_variables

    def get_output_variables(self) -> Set[str]:
        return set(self.output_variable_to_topology.keys())

    def get_topologies(self) -> Set[CrossbarTopology]:
        return set(self.output_variable_to_topology.values())

    def draw_dot(self, name: str):
        i = 0
        for topology in self.get_topologies():
            topology.draw_dot(name + "_{}".format(i))
            i += 1

    def write_xbar(self) -> str:
        content = ""
        for topology in self.get_topologies():
            content += topology.write_xbar()
        return content

    def add_topology(self, crossbar_topology: CrossbarTopology):
        for output_variable in crossbar_topology.get_output_variables():
            self.output_variable_to_topology[output_variable] = crossbar_topology
        self.input_variables.update(crossbar_topology.get_input_variables())
        # self.output_variables.update(crossbar_topology.get_output_variables())

    def eval(self, instance: Dict[str, bool]) -> Dict[str, bool]:
        evaluations = dict()
        for output_variable in self.output_variable_to_topology.keys():
            evaluations[output_variable] = False
        for output_variable, topology in self.output_variable_to_topology.items():
            evaluation = topology.eval(instance)
            value = evaluation[output_variable]
            if value:
                evaluations[output_variable] = True
        return evaluations
