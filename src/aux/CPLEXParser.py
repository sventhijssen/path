from pulp import CPLEX_CMD

from aux import config


class CPLEXParser:

    def __init__(self, solution_file_path):
        self.labeling = dict()
        self.solution_file_path = solution_file_path

    # def label(self):
    #     values = dict()
    #
    #     with open(str(self.solution_file_path), 'r') as f:
    #         content = f.read()
    #         key_values = re.findall(
    #             '<variable name="(x_\d+_[V|H])" index="\d+" status="\w+" value="([\d\.]+)" reducedCost="\d+"\/>',
    #             content)
    #         for (key, value) in key_values:
    #             if value != '0' or value != '1':
    #                 print(value)
    #             values[key] = int(round(float(value)))
    #
    #     for (key, value) in values.items():
    #         if key.startswith('x'):
    #             [_, node, orientation] = key.split("_")
    #             self.labeling[node] = 0
    #             if int(round(value)) == 1 and orientation == 'V':
    #                 self.labeling[node] += 1
    #             if int(round(value)) == 1 and orientation == 'H':
    #                 self.labeling[node] += -1
    #
    #     return self.labeling

    def label(self):
        solver = CPLEX_CMD(path=config.cplex_path, msg=False)
        status, values, reducedCosts, shadowPrices, slacks, solStatus = solver.readsol(str(self.solution_file_path))

        vertical = []
        horizontal = []
        for (key, value) in values.items():
            if key.startswith('x'):
                [_, node, orientation] = key.split("_")
                self.labeling[node] = 0
                if int(round(value)) == 1 and orientation == 'V':
                    vertical.append(node)
                if int(round(value)) == 1 and orientation == 'H':
                    horizontal.append(node)

        vertical_set = set(vertical)
        horizontal_set = set(horizontal)
        odd_cycle_transversal = vertical_set.intersection(horizontal_set)
        vs = len(vertical_set - odd_cycle_transversal)
        hs = len(horizontal_set - odd_cycle_transversal)
        vhs = len(odd_cycle_transversal)

        config.log.add("Label V: {}\n".format(vs))
        config.log.add("Label H: {}\n".format(hs))
        config.log.add("Label VH: {}\n".format(vhs))

        return vertical, horizontal
