benchmarks = [
    # ('ryy6.pla', False),
    # ('parity.pla', False),
    # ('pcler8.pla', True),
    # ('t481.pla', False),
    # ('cm150a.pla', False),
    # ('misex1.pla', True),
    # ('cmb.pla', True),
    # ('cm163a.pla', True),
    # ('5xp1.pla', True),
    # ('cordic.pla', True),
    # ('frg1.pla', True),
    # ('clip.pla', True),
    # ('ham15.pla', True),
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

alphas = [0.5]

collect_log_file_name = 'results.csv'

content = ''

for (benchmark, is_sbdd) in benchmarks:
    i = 0
    for alpha in alphas:
        if is_sbdd:
            bdd = "sbdd"
        else:
            bdd = "robdd"

        log_file_name = benchmark + '_' + bdd + '_' + str(alpha) + '.txt'

        K = 0
        N = 0
        I = 0
        gap = 0
        partition_time = 0

        with open(str(log_file_name), 'r') as f:
            for line in f.readlines():
                if "Partition K:" in line:
                    [_, raw_value] = line.split(":")
                    K += int(raw_value.replace(' ', ''))

                if "N:" in line:
                    [_, raw_value] = line.split(":")
                    N += int(raw_value.replace(' ', ''))

                if "I:" in line:
                    [_, raw_value] = line.split(":")
                    I += int(raw_value.replace(' ', ''))

                if "Gap (%):" in line:
                    [_, raw_value] = line.split(":")
                    gap += float(raw_value.replace(' ', ''))

                if "Partition ILP time (s):" in line:
                    [_, raw_value] = line.split(":")
                    partition_time += float(raw_value.replace(' ', ''))

        content += '{}\t{}\t{}\t{}\t{}'.format(K, N, I, gap, partition_time)

        if i == len(alphas) - 1:
            content += '\n'
        else:
            content += '\t'
        i += 1


with open(str(collect_log_file_name), 'w') as f:
    f.write(content)
