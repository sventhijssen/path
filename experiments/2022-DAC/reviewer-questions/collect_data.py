benchmark_filenames = [
    'in0.pla',
    'apex2.pla',
    'spla.pla',
    'pdc.blif',
    'misex3.pla',
    'tial.pla',
    'apex4.pla',
    'cps.pla',
    'apex5.pla',
    'seq.pla'
]

content = ""

for benchmark_filename in benchmark_filenames:
    [benchmark_name, _] = benchmark_filename.split('.')
    log_filename = "{}.log".format(benchmark_name)

    rows = 0
    columns = 0
    with open(log_filename, 'r') as f:
        for line in f.readlines():
            if line.startswith("Layer 0:"):
                [_, raw_value] = line.split(':')
                rows = int(raw_value)
            if line.startswith("Layer 1:"):
                [_, raw_value] = line.split(':')
                columns = int(raw_value)
    content += "{}\t{}\n".format(rows, columns)

with open("data.log", 'w') as f:
    f.write(content)
