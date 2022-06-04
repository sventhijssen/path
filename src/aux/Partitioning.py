from abc import ABC, abstractmethod

from core.GraphTopology import GraphTopology


class Partitioning(ABC):

    @abstractmethod
    def partition(self) -> GraphTopology:
        pass
