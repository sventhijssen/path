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

alpha = 0

collect_log_file_name = 'bdd_data.csv'

content = ''

bdds = ["sbdd"]

for benchmark in benchmarks:
    i = 0
    for bdd in bdds:

        log_file_name = benchmark + '_' + bdd + '_' + str(bdd) + '.log'

        nodes = 0
        edges = 0

        with open(str(log_file_name), 'r') as f:
            for line in f.readlines():

                if "\tNodes:" in line:
                    [_, raw_value] = line.split(":")
                    nodes += int(raw_value.replace(' ', ''))

                if "\tEdges:" in line:
                    [_, raw_value] = line.split(":")
                    edges += int(raw_value.replace(' ', ''))

        content += '{}\t{}'.format(nodes, edges)

        if i == len(bdds) - 1:
            content += '\n'
        else:
            content += '\t'
        i += 1


with open(str(collect_log_file_name), 'w') as f:
    f.write(content)
