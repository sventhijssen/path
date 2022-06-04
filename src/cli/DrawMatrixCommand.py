from aux import config
from cli.Command import Command


class DrawMatrixCommand(Command):

    def __init__(self, args: list):
        super(DrawMatrixCommand).__init__()
        if len(args) > 0:
            self.name = args[0]
        else:
            raise Exception("Name must be provided.")

        if "-dot" in args:
            self.draw_dot = True
        else:
            self.draw_dot = False

    def execute(self):
        context = config.context_manager.get_context()

        boolean_function = context.boolean_function

        if self.draw_dot:
            boolean_function.draw_dot(self.name)
        else:
            boolean_function.draw_matrix(self.name)

        # for i in range(len(context.crossbars)):
        #     crossbar = context.crossbars[i]
        #     crossbar.draw_matrix("{}_{}".format(self.name, i))
        return False
