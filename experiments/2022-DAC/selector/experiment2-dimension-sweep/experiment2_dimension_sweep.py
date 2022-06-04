from cli.Program import Program

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
    # ('in0.pla', True),
    # ('apex2.pla', True),
    # ('spla.pla', True),
    # ('pdc.pla', True),
    # ('misex3.pla', True),
    # ('tial.pla', True),
    # ('apex4.pla', True),
    # ('cps.pla', True),
    # ('apex5.cnf.pla', True),
    ('seq.pla', True),
]

Ds = [128, 256, 512, 1024]
alpha = 0.5
time_limit = 3600  # seconds

for D in Ds:
    for (benchmark, sbdd) in benchmarks:
        if sbdd:
            bdd = "sbdd"
        else:
            bdd = "robdd"

        log_file_name = benchmark + '_' + bdd + '_' + str(D) + '.txt'
        raw_command = 'new_log {} | read benchmarks/{} | {} -m | partition {} -a {} -t {}'.format(log_file_name, benchmark, bdd, D, alpha, time_limit)

        try:
            Program.execute(raw_command)
        except Exception as e:
            print(e)
