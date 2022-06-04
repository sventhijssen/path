import os
from pathlib import Path

from src.cli import Program

benchmark = "example.v"

path = Path(os.getcwd())
benchmark_path= path.joinpath(benchmark)
log_file_name = 'example.log'
raw_command = 'new_log {} | read {} | robdd -m | path | draw_matrix'.format(log_file_name, benchmark_path)

try:
    Program.execute(raw_command)
except Exception as e:
    print(e)
