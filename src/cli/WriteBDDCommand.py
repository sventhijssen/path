from aux import config
from aux.BDDWriter import BDDWriter
from cli.Command import Command


class WriteBDDCommand(Command):

    def __init__(self, args):
        super(WriteBDDCommand).__init__()
        if len(args) < 1:
            raise Exception("File name must be defined.")
        self.file_name = args[0]

    def execute(self) -> bool:
        context = config.context_manager.get_context()
        w = BDDWriter(context.boolean_function.name, self.file_name)
        w.write(context.benchmark_graph)
        return False
