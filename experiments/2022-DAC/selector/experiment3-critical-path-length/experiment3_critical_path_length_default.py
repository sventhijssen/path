import os
from pathlib import Path

from networkx import Graph, DiGraph, dag_longest_path_length

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

alpha = 0.5

collect_log_file_name = "default.csv"

content = ""

for (benchmark, sbdd) in benchmarks:
    if sbdd:
        bdd = "sbdd"
    else:
        bdd = "robdd"

    relative_path = Path(os.getcwd()).parent.joinpath("experiment1-default")
    log_file_name = benchmark + '_' + bdd + '_' + str(alpha) + ".txt"
    log_file_path = relative_path.joinpath(log_file_name)
    crossbar_nodes = dict()
    crossbar_edges = dict()
    with open(log_file_path, "r") as f:
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
    print(k)
    # print(roots)
    # print(terminal)
    # print(crossbar_edges)
    # print(crossbar_nodes)

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

    digraph = DiGraph()
    terminal_crossbars = list(node_crossbars[terminal])
    print("Terminal crossbars: {}".format(terminal_crossbars))
    # print(terminal_crossbars)
    # if len(terminal_crossbars) > 1:
    #     raise Exception("Multiple start crossbars.")
    q = terminal_crossbars
    visited = set()
    while len(q) != 0:
        crossbar = q.pop()
        visited.add(crossbar)
        connections = crossbar_connections[crossbar]
        for connection in connections:
            if connection not in visited:
                intersection = set(crossbar_nodes[crossbar]).intersection(set(crossbar_nodes[connection]))
                q.append(connection)
                digraph.add_edge(crossbar, connection)

    graph = Graph()
    for i in range(len(crossbar_nodes)):
        for j in range(i + 1, len(crossbar_nodes)):
            intersection = set(crossbar_nodes[i]).intersection(set(crossbar_nodes[j]))
            if len(intersection) > 0:
                graph.add_edge(i, j)
                # print("{}-{}".format(i, j))

    # draw(digraph)
    # plt.show()
    longest_path = dag_longest_path_length(digraph)  # In terms of edges
    print("Number of crossbars: {}".format(len(crossbar_nodes)))
    print("Longest path length: {}".format(longest_path + 1))  # In terms of nodes
    # print(len(digraph.nodes))
    # print(len(digraph.edges))
    # print(len(graph.nodes))
    # print(len(graph.edges))
    print()

    content += '{}\n'.format(longest_path + 1)  # In terms of nodes

with open(str(collect_log_file_name), 'w') as f:
    f.write(content)
