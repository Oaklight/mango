import itertools
from digraph import build_graph_from_file, plot_graph, get_all_paths, print_all_paths

g = build_graph_from_file('../data/zork1.map',
                          '../data/zork1.actions')
plot_graph(g)

# generate pair-wise all paths between all nodes
# get generator of zip of any two different nodes from graph
all_pairs = list(itertools.combinations(g.nodes(), 2))
# print(all_pairs)

for srcNode, dstNode in all_pairs:
    allPaths = get_all_paths(g, src=srcNode, dst=dstNode)
    print_all_paths(g, allPaths, verbose=False, diff_shortest=True)