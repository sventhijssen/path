from datetime import datetime

from aux import config
from aux.CPLEXParser import CPLEXParser
from cli.Command import Command


class ReadCPLEXCommand(Command):

    def __init__(self, args: list):
        super(ReadCPLEXCommand).__init__()
        if len(args) < 1:
            raise Exception("No file defined.")
        self.file_path = args[0]

    def execute(self):
        print("COMPACT started using CPLEX solution")
        print(datetime.now())

        cplex_parser = CPLEXParser(self.file_path)

        vertical, horizontal = cplex_parser.label()

        rows = len(horizontal)
        columns = len(vertical)
        config.log.add('Rows: {}\n'.format(rows))
        config.log.add('Columns: {}\n'.format(columns))

        print("COMPACT stopped using CPLEX solution")
