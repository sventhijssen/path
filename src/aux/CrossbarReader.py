import re
from pathlib import Path

from core.Literal import Literal
from core.MemristorCrossbar import MemristorCrossbar
from core.SelectorCrossbar import SelectorCrossbar


class CrossbarReader:

    def __init__(self, file_name: str):
        self.file_name = file_name
        self.crossbar = None

    def _get_model(self):
        pass

    @staticmethod
    def _get_input_variables(line):
        return line.split(" ")[1:]

    @staticmethod
    def _get_input_nanowires(lines):
        input_nanowires = dict()
        for line in lines:
            line_lst = line.split(" ")
            if line_lst[0] != ".i":
                break
            input_nanowires[line_lst[1]] = (0, int(line_lst[2]))
        return input_nanowires

    @staticmethod
    def _get_output_variables(lines):
        output_variables = dict()
        for line in lines:
            line_lst = line.split(" ")
            if line_lst[0] == ".xbar":
                break
            if line_lst[0] == ".o":
                output_variables[line_lst[1]] = (0, int(line_lst[2]))
        return output_variables

    def read(self):
        # TODO: Fix layers for input nanowires and output nanowires
        inter_connections = []
        crossbars_data = []
        crossbar_data = None

        with open(self.file_name, 'r') as f:
            for line in f.readlines():
                if line.startswith(".xbar "):
                    if crossbar_data is not None:
                        crossbars_data.append(crossbar_data)

                    crossbar_data = dict()

                    attributes = line.split()
                    if len(attributes) > 1:
                        name = attributes[1]
                    else:
                        name = 0

                    if len(attributes) > 2:
                        xbar_type = attributes[2]
                    else:
                        xbar_type = "1D1M"

                    crossbar_data["name"] = name
                    crossbar_data["xbar_type"] = xbar_type

                elif line.startswith(".r "):
                    (_, raw_value) = line.split()
                    rows = int(raw_value)
                    crossbar_data["rows"] = rows

                elif line.startswith(".l "):
                    (_, raw_value) = line.split()
                    layers = int(raw_value)
                    crossbar_data["layers"] = layers

                elif line.startswith(".c "):
                    (_, raw_value) = line.split()
                    columns = int(raw_value)
                    crossbar_data["columns"] = columns

                elif line.startswith(".input "):
                    raw_values = line.split()
                    input_variables = raw_values[1:]
                    crossbar_data["input_variables"] = input_variables

                elif line.startswith(".output "):
                    raw_values = line.split()
                    output_variables = raw_values[1:]
                    crossbar_data["output_variables"] = output_variables

                elif line.startswith(".i "):
                    (_, variable, raw_layer, raw_index) = line.split()
                    if "input_nanowires" not in crossbar_data:
                        crossbar_data["input_nanowires"] = dict()
                    crossbar_data["input_nanowires"][variable] = (int(raw_layer), int(raw_index))

                elif line.startswith(".o "):
                    (_, variable, raw_layer, raw_index) = line.split()
                    if "output_nanowires" not in crossbar_data:
                        crossbar_data["output_nanowires"] = dict()
                    crossbar_data["output_nanowires"][variable] = (int(raw_layer), int(raw_index))

                elif line.startswith(".s "):
                    (_, raw_layer, raw_index, element) = line.split()
                    if element == "0":
                        literal = Literal("False", False)
                    elif element == "1":
                        literal = Literal("True", True)
                    elif element.startswith("~"):
                        atom = element.replace("~", "")
                        literal = Literal(atom, False)
                    else:
                        atom = element
                        literal = Literal(atom, True)

                    if "literals" not in crossbar_data:
                        crossbar_data["literals"] = [literal]
                    else:
                        crossbar_data["literals"].append(literal)

                elif line.startswith(".ic "):
                    (_, x0_name, l0, i0, x1_name, l1, i1) = line.split()
                    inter_connections.append(((x0_name, l0, i0), (x1_name, l1, i1)))

                elif not line.startswith(".") and not line.strip() == "":
                    if "matrix" not in crossbar_data:
                        crossbar_data["matrix"] = [line.split()]
                    else:
                        crossbar_data["matrix"].append(line.split())

            crossbars_data.append(crossbar_data)

        # self.crossbar = MemristorCrossbar(rows, columns)
        # self.crossbar.input_variables = input_variables
        # self.crossbar.output_nanowires = output_variables
        # self.crossbar.filename = Path(self.file_name)
        # self.crossbar.name = Path(lines[0].split(" ")[1]).name
        # self.crossbar.input_nanowires = input_nanowires

        # file_offset = lines.index(".xbar")
        # for r in range(rows):
        #     line = lines[file_offset+1+r].split('\t')
        #     for c in range(columns):
        #         raw_literal = re.findall(r'(0|1|[\[\]a-z0-9]+|\\\+[\[\]a-z0-9]+)', line[c])[0]
        #         if raw_literal == '0':
        #             self.crossbar.set_memristor(r, c, Literal('False', False))
        #         elif raw_literal == '1':
        #             self.crossbar.set_memristor(r, c, Literal('True', True))
        #         elif raw_literal[0] == '\\':
        #             self.crossbar.set_memristor(r, c, Literal(raw_literal[2:], False))
        #         else:
        #             self.crossbar.set_memristor(r, c, Literal(raw_literal, True))

        crossbars = []

        for crossbar_data in crossbars_data:
            name = crossbar_data["name"]
            xbar_type = crossbar_data["xbar_type"]
            rows = crossbar_data["rows"]
            columns = crossbar_data["columns"]
            literals = crossbar_data["literals"]
            matrix = crossbar_data["matrix"]

            if xbar_type == "1D1M":
                crossbar = MemristorCrossbar(rows, columns)
            elif xbar_type == "1T1M":
                crossbar = SelectorCrossbar(rows, columns)

            crossbar.name = name
            crossbar.input_variables = crossbar_data["input_variables"]
            crossbar.output_variables = crossbar_data["output_variables"]
            crossbar.input_nanowires = crossbar_data["input_nanowires"]
            crossbar.output_nanowires = crossbar_data["output_nanowires"]
            crossbar.literals = literals

            for r in range(rows):
                for c in range(columns):
                    element = matrix[r][c]
                    if element == "0":
                        literal = Literal("False", False)
                    elif element == "1":
                        literal = Literal("True", True)
                    elif element.startswith("~"):
                        atom = element.replace("~", "")
                        literal = Literal(atom, False)
                    else:
                        atom = element
                        literal = Literal(atom, True)
                    crossbar.set_memristor(r, c, literal)

            crossbars.append(crossbar)

        return crossbars, inter_connections
