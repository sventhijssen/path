import random
from typing import Set, List

from core.Literal import Literal
from core.MemristorCrossbar import MemristorCrossbar


class FaultyCrossbarGenerator:

    def __init__(self, rows: int, columns: int, nr: int, stuck_on_percentage: float = 0, stuck_off_percentage: float = 0,
                 stuck_on: int = 0, stuck_off: int = 0, seed: int = 42):
        self.rows = rows
        self.columns = columns

        if not stuck_on_percentage and not stuck_on:
            self.stuck_on = 0
            self.stuck_on_percentage = self.stuck_on / (rows*columns)
        elif not stuck_on_percentage and stuck_on:
            self.stuck_on = stuck_on
            self.stuck_on_percentage = self.stuck_on / (rows*columns)
        elif stuck_on_percentage and not stuck_on:
            self.stuck_on = int(stuck_on_percentage * rows * columns)
            self.stuck_on_percentage = stuck_on_percentage
        else:
            self.stuck_on = stuck_on_percentage * rows * columns
            self.stuck_on_percentage = stuck_on_percentage

        if not stuck_off_percentage and not stuck_off:
            self.stuck_off = 0
            self.stuck_off_percentage = self.stuck_off / (rows*columns)
        elif not stuck_off_percentage and stuck_off:
            self.stuck_off = stuck_off
            self.stuck_on_percentage = self.stuck_off / (rows*columns)
        elif stuck_off_percentage and not stuck_off:
            self.stuck_off = int(stuck_off_percentage * rows * columns)
            self.stuck_off_percentage = self.stuck_off / (rows*columns)
        else:
            self.stuck_off = stuck_off_percentage * rows * columns
            self.stuck_off_percentage = stuck_off_percentage

        self.nr = nr
        self.seed = seed

    def _de_linearize(self, positions: List[int]) -> Set:
        return set(map(lambda k: (k // self.columns, k % self.columns), positions))

    def generate(self):
        random.seed(self.seed)

        for i in range(self.nr):

            total_memristors = self.rows * self.columns

            available_memristors = set([i for i in range(total_memristors)])

            # nr_stuck_on = int(self.stuck_on_percentage * total_memristors)
            # nr_stuck_off = int(self.stuck_off_percentage * total_memristors)

            stuck_on = random.sample(list(available_memristors), k=self.stuck_on)
            available_memristors.difference_update(stuck_on)

            stuck_off = random.sample(list(available_memristors), k=self.stuck_off)

            stuck_on_positions = self._de_linearize(stuck_on)
            stuck_off_positions = self._de_linearize(stuck_off)

            crossbar = MemristorCrossbar(self.rows, self.columns)

            for r in range(self.rows):
                for c in range(self.columns):
                    crossbar.set_memristor(r, c, Literal('-', True))

            for (r, c) in stuck_on_positions:
                crossbar.set_memristor(r, c, Literal('True', True))
                crossbar.get_memristor(r, c).stuck_at_fault = True

            for (r, c) in stuck_off_positions:
                crossbar.set_memristor(r, c, Literal('False', False))
                crossbar.get_memristor(r, c).stuck_at_fault = True

            yield crossbar
