## Command line

Using command line, one can run the program using the following template:

If no BDD is available:
```bash
python3 cli/main.py new_log LOG_NAME | read BENCHMARK_NAME | BDD_TYPE | write_bdd BDD_FILENAME | path 
```

If a BDD is available:
```bash
python3 cli/main.py new_log LOG_NAME | read_bdd BDD_FILENAME | path 
```

### Log file
It is best to record your experiments with a log. To set up a new log, use ```new_log LOG_FILENAME```. It is best practice to use the file extension ``.log``. Note that a log file will be overridden when the same log name is used.

### Benchmark
Benchmarks are located in the folder [_benchmarks_](/benchmarks).
Depending on the OS, locate the relative file path as follows (make sure to use the correct file separator `\ ` or `/ `):

```
benchmarks/5xp1.pla
```

### BDD type
Two BDD types can be used: ```robdd``` and ```sbdd```.

### BDD file
One can write a BDD to file using the command ```write_bdd BDD_FILENAME```. It is best practice to use the file extension ``.bdd``.

### PATH
PATH does not have any optional arguments.

### Partitioning
One can partition a BDD using the command ```partition DIMENSION```. Usually DIMENSION is a power of two (128, 256, 512, ....).
This command can be called using optional arguments.

##### Alpha
Alpha is value between [0,1]. By default, alpha is 0.5. Determines the amount of pressure towards minimizing the number of crossbars and the number of inter-crossbar connections.
When alpha is 0, then the number of crossbars is optimized. When alpha is one, then the number of inter-crossbar connections is optimized.
Otherwise, a weighted sum of both is optimized.
```bash
-a VALUE
```

##### Overestimate
One can define an overestimate on the maximum number of crossbars. By default, the overestimate is 1.2 x max(|V|, |E|) where |V| and |E| are the number of nodes and edges of the BDD, respectively.
```bash
-k VALUE
```

##### Timeout
One can define a timeout on the ILP formulation. The duration for the timeout is defined in seconds. By default, the timeout is unlimited.
```bash
-t VALUE
```

## Examples
Below, a small set of examples is provided:

```bash
python3 cli/main.py new_log t481.log | read benchmarks/t481.pla | robdd -m | path
```

```bash
python3 cli/main.py new_log t481.log | read benchmarks/t481.pla | sbdd | path
```

```bash
python3 cli/main.py new_log t481.log | read_bdd t481.bdd | partition 128 -k 10 -t 3600
```