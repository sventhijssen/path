from matplotlib import pyplot as plt
from networkx import Graph, draw, diameter, DiGraph, dag_longest_path_length

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
            print("{}-{}: {}".format(i, j, intersection))

draw(digraph)
plt.show()
longest_path = dag_longest_path_length(digraph)  # In terms of edges
print("Number of crossbars: {}".format(len(crossbar_nodes)))
print("Longest path length: {}".format(longest_path + 1))  # In terms of nodes
# print(len(digraph.nodes))
# print(len(digraph.edges))
# print(len(graph.nodes))
# print(len(graph.edges))
print()
