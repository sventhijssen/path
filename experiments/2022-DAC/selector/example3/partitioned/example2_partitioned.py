import os
from pathlib import Path

from cli.Program import Program

D = 4
alpha = 0
time_limit = 600  # seconds
benchmark = "example.v"

path = Path(os.getcwd())
benchmark_path= path.joinpath(benchmark)
log_file_name = 'example.log'
raw_command = 'new_log {} | read {} | robdd -m | partition {} -a {} -t {} | path | draw_matrix'.format(log_file_name, benchmark_path, D, alpha, time_limit)

try:
    Program.execute(raw_command)
except Exception as e:
    print(e)
