class VerilogGenerator:

    @staticmethod
    def write_verilog(file_name, input_variables, output_variables, formulas):
        with open(file_name, 'w') as f:
            f.write('module f ({});\n'.format(", ".join(input_variables) + ", " + ", ".join(output_variables)))
            f.write('input\t {};\n'.format(", ".join(input_variables)))
            f.write('output\t {};\n'.format(", ".join(output_variables)))
            for formula in formulas:
                f.write('assign {};\n'.format(formula))
            f.write('endmodule')
