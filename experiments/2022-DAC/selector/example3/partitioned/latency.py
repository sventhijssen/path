from pulp import CPLEX_CMD, LpVariable, LpInteger, LpProblem, LpMinimize, LpStatusInfeasible

from aux import config

alpha = 0.5

content = ""

log_file_name = "example.log"

crossbar_nodes = dict()
crossbar_edges = dict()
with open(log_file_name, "r") as f:
    k = -1
    nodes = None
    edges = None
    roots = None
    terminal = None
    for line in f.readlines():
        if line.startswith("\tCrossbar"):
            k += 1
        elif line.startswith("\tNodes") and k >= 0:
            [_, raw_value] = line.split(":")
            nodes = eval(raw_value.replace(' ', ''))
            crossbar_nodes[k] = nodes
        elif line.startswith("\tEdges") and k >= 0:
            [_, raw_value] = line.split(":")
            edges = eval(raw_value.replace(' ', ''))
            crossbar_edges[k] = edges

        if line.startswith("Roots"):
            [_, raw_value] = line.split(":")
            roots = eval(raw_value.replace(' ', ''))
        if line.startswith("Terminal"):
            [_, raw_value] = line.split(":")
            terminal = eval(raw_value.replace(' ', ''))[0]

node_crossbars = dict()
for (crossbar, nodes) in crossbar_nodes.items():
    for node in nodes:
        if node not in node_crossbars:
            node_crossbars[node] = [crossbar]
        else:
            node_crossbars[node].append(crossbar)

crossbar_connections = dict()
for i in range(len(crossbar_nodes)):
    crossbar_connections[i] = []
    for j in range(len(crossbar_nodes)):
        if i != j:
            intersection = set(crossbar_nodes[i]).intersection(set(crossbar_nodes[j]))
            if len(intersection) > 0:
                crossbar_connections[i].append(j)

print(crossbar_connections)

terminal_crossbars = list(node_crossbars[terminal])

solver = CPLEX_CMD(path=config.cplex_path, msg=False)

xbars = [i for i in range(len(crossbar_nodes))]
cmbs = []
for (xbar, connections) in crossbar_connections.items():
    for connection in connections:
        cmbs.append((xbar, connection))

# Time variables for each crossbar
t_vars = LpVariable.dicts("t", xbars, 0, cat=LpInteger)
d_vars = LpVariable.dicts("d", cmbs, cat=LpInteger)

# Maximum time
T = LpVariable("T", cat=LpInteger)

lpvc = LpProblem("VC", LpMinimize)

lpvc += T

for (xbar, connections) in crossbar_connections.items():
    for connection in connections:
        lpvc += t_vars[xbar] <= t_vars[connection] + d_vars[(xbar, connection)]
        lpvc += t_vars[xbar] <= T
        lpvc += d_vars[(xbar, connection)] != 0

terminal_crossbars = list(node_crossbars[terminal])
for xbar in terminal_crossbars:
    lpvc += t_vars[xbar] == 0

lpvc.solve(solver)

if lpvc.status == LpStatusInfeasible:
    print("Infeasible solution.")

print(T.varValue)