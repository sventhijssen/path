benchmarks = [
    ('in0.pla', True),
    ('apex2.pla', True),
    ('spla.pla', True),
    ('pdc.pla', True),
    ('misex3.pla', True),
    ('tial.pla', True),
    ('apex4.pla', True),
    ('cps.pla', True),
    ('apex5.cnf.pla', True),
    ('seq.pla', True),
]

collect_log_file_name = 'results.csv'

content = ''

for (benchmark, is_sbdd) in benchmarks:
    if is_sbdd:
        bdd = "sbdd"
    else:
        bdd = "robdd"

    log_file_name = benchmark + '_' + bdd + '_1_optimal.txt'

    with open(str(log_file_name), 'r') as f:
        for line in f.readlines():

            if line.startswith("Edges:"):
                [_, raw_value] = line.split(":")
                edges = float(raw_value.replace(' ', ''))

            if line.startswith("Rows:"):
                [_, raw_value] = line.split(":")
                rows = float(raw_value.replace(' ', ''))

    content += '{}\t{}\n'.format(edges, rows)


with open(str(collect_log_file_name), 'w') as f:
    f.write(content)
