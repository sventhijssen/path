import math
import time
from pathlib import Path

from z3 import Bool

from core.Benchmark import Benchmark
from core.BooleanFunction import BooleanFunction
from verf.EquivalenceChecker import EquivalenceChecker


class Enumeration(EquivalenceChecker):

    def __init__(self, boolean_function_a: BooleanFunction, boolean_function_b: BooleanFunction,
                 primary_input_path: Path = None):
        super().__init__(boolean_function_a, boolean_function_b)

        # TODO: Fix primary inputs
        self.primary_input_map = self._read_primary_input_map(primary_input_path)

    @staticmethod
    def _read_primary_input_map(primary_input_path: Path):
        primary_input_map = dict()

        if primary_input_path is None:
            return

        with open(str(primary_input_map), 'r') as f:
            for line in f.readlines():
                new, old = line.split()
                primary_input_map[old] = new

        return primary_input_map

    def is_equivalent(self, benchmark: Benchmark, sampling_size: int = -1) -> bool:
        print("Started enumeration")
        start_time = time.time()

        input_variables_a = set(self.boolean_function_a.get_input_variables())
        input_variables_b = set(self.boolean_function_b.get_input_variables())

        input_variables = list(input_variables_a.union(input_variables_b))

        output_variables_a = set(self.boolean_function_a.get_output_variables())
        output_variables_b = set(self.boolean_function_b.get_output_variables())
        output_variables = list(output_variables_a.union(output_variables_b))

        n = len(input_variables)

        for i in range(int(math.pow(2, n))):
            print("\t{}/{}".format(i + 1, int(math.pow(2, n))))
            binary_string = format(int(i), '0' + str(n) + 'b')
            instance = {}
            for j in range(n):
                input_variable = input_variables[j]
                instance[input_variable] = bool(int(binary_string[n - j - 1]))

            evaluation_a = self.boolean_function_a.eval(instance)
            evaluation_b = self.boolean_function_b.eval(instance)

            for output_variable in output_variables:
                if evaluation_a[output_variable] != evaluation_b[output_variable]:
                    print("Not equivalent.")
                    print(output_variable)
                    print(instance)
                    print(evaluation_a[output_variable])
                    print(evaluation_b[output_variable])
                    print("Stopped enumeration")
                    print()
                    return False

        print("Equivalent.")
        print("Stopped enumeration")
        print()
        return True

    def to_formula(self, output_variable: str) -> Bool:
        pass
