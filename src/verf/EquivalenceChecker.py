from abc import ABC, abstractmethod

from timeout_decorator import timeout_decorator
from z3 import Bool

from aux import config
from core.Benchmark import Benchmark
from core.BooleanFunction import BooleanFunction


class EquivalenceChecker(ABC):

    @abstractmethod
    def __init__(self, boolean_function_a: BooleanFunction, boolean_function_b: BooleanFunction):
        self.boolean_function_a = boolean_function_a
        self.boolean_function_b = boolean_function_b
        self.execution_time = []
        self.formulae = dict()  # A dictionary <output_variable: str, formula: Bool>
        self.return_formulae = True
        self.formula_sizes = dict()

    def get_execution_time(self):
        return self.execution_time

    @abstractmethod
    @timeout_decorator.timeout(config.equivalence_checker_timeout)
    def is_equivalent(self, benchmark: Benchmark, sampling_size: int = -1) -> bool:
        pass

    @abstractmethod
    def to_formula(self, output_variable: str) -> Bool:
        pass
