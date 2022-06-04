import pathlib
import platform
import sys

from cli.ContextManager import ContextManager
from aux.Log import Log

context_manager = ContextManager()
verbose = True
log = Log()
clean = True

# Settings for BDD
time_limit_bdd = 60
bdd = "robdd"
bdd_parser = None
full_bdd = False

module = None
trace = True

# Apply a time limit to partitioning
time_limit_partition = None

# Settings for COMPACT
# Apply input and output constraints
io_constraints = True
# Input layer
input_layer = None
# Output layer
output_layer = None
# Apply a time limit
time_limit = None
# Keep auxiliary files from CPLEX
keep_files = False
# By default, the objective of COMPACT is to optimize the semiperimeter (only for K-labeling)
# Other option = "cs" for "constraint solving" (no minimization)
objective = "semi"
gamma = 1
max_rows = sys.maxsize
max_columns = sys.maxsize

mapping_method = "compact"

root = pathlib.Path(__file__).parent.parent.parent.absolute()
benchmark_path = root.joinpath('benchmarks')
abc_path = root.joinpath('abc')
plot_signal = False

crossbar_id = 0

if platform.system() == 'Windows':
    bash_cmd = ['bash', '-c']
    cplex_path = '/opt/ibm/ILOG/CPLEX_Studio201/cplex/bin/x64_win64/cplex.exe'
elif platform.system() == 'Linux':
    bash_cmd = ['/bin/bash', '-c']
    cplex_path = '/opt/ibm/ILOG/CPLEX_Studio201/cplex/bin/x86-64_linux/cplex'
elif platform.system() == 'Darwin':
    bash_cmd = ['/bin/bash', '-c']
    cplex_path = '/Applications/CPLEX_Studio201/cplex/bin/x86-64_osx/cplex'
else:
    raise Exception("Unsupported OS: {}".format(platform.system()))

library_path = root.joinpath("library")

abc_cmd = bash_cmd.copy()
abc_cmd.extend(['"./abc"'])
abc_cmd = ' '.join(abc_cmd)
clang_cmd = "clang"
equivalence_checker_timeout = 3600
