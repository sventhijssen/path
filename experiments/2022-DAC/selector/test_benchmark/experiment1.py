from cli.Program import Program

benchmarks = [
    # ('parity.pla', False),
    # ('cm150a.pla', False),
    # ('t481.pla', False),
    # ('cm162a.blif', True),
    # ('x2.pla', True),
    # ('cm163a.pla', True),
    # ('misex1.pla', True),
    # ('cordic.pla', True),
    # ('5xp1.pla', True),
    # ('clip.pla', True),
    # ('alu4.pla', True),
    # ('misex3.pla', True),
    # ('apex2.pla', True),
    # ('seq.pla', True),
    # ('frg1.pla', True),
    # ('spla.pla', True),
    # ('cps.pla', True),
    # ('e64.pla', True),
    # ('apex5.cnf.pla', True),
    ('bc0.pla', True)
]

alpha = 0.5
timeout = 600

for (benchmark_file_name, is_sbdd) in benchmarks:
    if is_sbdd:
        bdd = "sbdd"
    else:
        bdd = "robdd"

    log_file_name = benchmark_file_name + '.log'
    k = 12
    d = 128
    raw_command = 'new_log {} | read benchmarks/{} | {} -m | partition {} -k {} -alpha {} -t {}'.format(log_file_name, benchmark_file_name, bdd, d, k, alpha, timeout)
    Program.execute(raw_command)
