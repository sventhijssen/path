benchmarks = [
    'in0.pla',
    'apex2.pla',
    'spla.pla',
    'pdc.pla',
    'misex3.pla',
    'tial.pla',
    'apex4.pla',
    'cps.pla',
    'apex5.cnf.pla',
    'seq.pla',
]

arche_log_file_name = 'log.txt'
collect_log_file_name = 'results.csv'

arche_stats = dict()
with open(str(arche_log_file_name), 'r') as f:
    for line in f.readlines():
        if not line.startswith("DEBUG"):
            benchmark_stats = eval(line)
            arche_stats[benchmark_stats.get("benchmark")] = benchmark_stats

content = ''

for benchmark in benchmarks:
    benchmark_name, _ = benchmark.split(".")
    print(benchmark_name)
    benchmark_blif = "{}.blif".format(benchmark_name)
    if benchmark_blif in arche_stats:
        benchmark_stats = arche_stats.get("{}.blif".format(benchmark_name))
        operations = benchmark_stats.get("opcount")
        operation_count = sum(operations.values())
        cycles = benchmark_stats.get("opcycles")
        cycle_count = sum(cycles.values())
        content += '{}\t{}\n'.format(operation_count, cycle_count)
    else:
        content += '\n'

with open(str(collect_log_file_name), 'w') as f:
    f.write(content)
