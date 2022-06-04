from cli.Program import Program

benchmarks = [
    'in0.pla',
    'apex2.pla',
    'spla.pla',
    'pdc.pla',
    'misex3.pla',
    'tial.pla',
    # 'apex4.pla',
    'cps.pla',
    # 'apex5.cnf.pla',
    # 'seq.pla',
]

bdds = ["robdd", "sbdd"]

for bdd in bdds:
    for benchmark in benchmarks:

        log_file_name = benchmark + '_' + bdd + '_' + str(bdd) + '.log'
        raw_command = 'new_log {} | read benchmarks/{} | {} -m'.format(log_file_name, benchmark, bdd)

        try:
            Program.execute(raw_command)
        except Exception as e:
            print(e)
