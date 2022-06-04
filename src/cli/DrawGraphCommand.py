from aux import config
from cli.Command import Command


class DrawGraphCommand(Command):

    def __init__(self, args: list):
        super().__init__()
        self.args = args

    def execute(self):
        context = config.context_manager.get_context()
        context.crossbars.draw_graph(context.benchmark.name)
        return False
