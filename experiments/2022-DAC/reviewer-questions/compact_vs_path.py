from aux import config
from cli.Program import Program

benchmark_filenames = [
    # 'in0.pla',
    # 'apex2.pla',
    # 'spla.pla',
    # 'pdc.pla',
    'misex3.pla',
    # 'tial.pla',
    # 'apex4.pla',
    # 'cps.pla',
    # 'apex5.pla',
    # 'seq.pla'
]

for benchmark_filename in benchmark_filenames:
    # benchmark_filepath = config.root.joinpath("benchmarks").joinpath("revlib").joinpath(benchmark_filename)
    benchmark_filepath = config.root.joinpath("benchmarks").joinpath(benchmark_filename)
    [benchmark_name, _] = benchmark_filename.split('.')
    log_filename = "{}.log".format(benchmark_name)
    program = Program()
    program.execute("new_log {} | read {} | sbdd | compact".format(log_filename, benchmark_filepath))