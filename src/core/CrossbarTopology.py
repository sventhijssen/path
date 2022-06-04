from abc import abstractmethod
from typing import Dict

from core.BooleanFunction import BooleanFunction


class CrossbarTopology(BooleanFunction):

    @abstractmethod
    def write_xbar(self) -> str:
        pass

    @abstractmethod
    def eval(self, instance: Dict[str, bool]) -> Dict[str, bool]:
        pass

    @abstractmethod
    def draw_dot(self, name: str):
        pass
