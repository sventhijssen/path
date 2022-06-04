import os
from pathlib import Path

from cli.Program import Program

benchmark_name = "adder2"
bdd = "sbdd"

directory = Path(os.getcwd())

benchmark_file_name = directory.joinpath(benchmark_name + ".pla")
pdf_file_name = benchmark_name
log_file_name = benchmark_name + '.log'
specification_file_name = directory.joinpath(benchmark_name + '_spec.v')

raw_command = 'new_log {} | read {} | {} -m | path | draw_matrix {} | enum {}'.format(log_file_name, benchmark_file_name, bdd, benchmark_name, specification_file_name)
Program.execute(raw_command)
