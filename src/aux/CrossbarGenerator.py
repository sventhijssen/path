import random
from itertools import product
from typing import List

from memx.Literal import Literal
from core.Memristor import Memristor


class CrossbarGenerator:

    @staticmethod
    def generate(nr_designs: int, rows: int, columns: int, variables: List[str], density: float, all_variables_at_least_once: bool, seed: int):

        if all_variables_at_least_once:
            if len(variables) > rows*columns:
                raise Exception("More variables than memristors")

        random.seed(seed)

        possibilities = [Literal('True', True)]
        possibilities.extend([Literal(variable, False) for variable in variables])
        possibilities.extend([Literal(variable, True) for variable in variables])

        for i in range(nr_designs):
            crossbar = [[Memristor(r, c, Literal('False', False)) for c in range(columns)] for r in range(rows)]

            visited_positions = set()
            k = int(rows*columns*density / 100)
            if all_variables_at_least_once:
                positions = list(product(range(rows), range(columns)))
                random.shuffle(positions)

                for j in range(len(variables)):
                    # For each variable, place its positive or negative variable randomly on the crossbar
                    variable = random.choice([Literal(variables[j], True), Literal(variables[j], False)])
                    position = positions[j]
                    r = position[0]
                    c = position[1]
                    crossbar[r][c] = Memristor(r, c, variable)
                    visited_positions.add(position)
                    k -= 1

            if k > 0:
                population = set(product(range(rows), range(columns)))
                remaining_population = population - visited_positions
                samples = random.sample(remaining_population, k)

                for r in range(rows):
                    for c in range(columns):
                        if (r, c) in samples:
                            if crossbar[r][c].literal.atom == 'False':
                                crossbar[r][c] = Memristor(r, c, random.choice(possibilities))
            yield crossbar
