import argparse
import itertools

from digraph import build_graph_from_file, get_shortest_path, plot_graph, print_path
from utils import inputColor, printColor

parser = argparse.ArgumentParser()
parser.add_argument("--map", type=str, default="../data/zork1.map")
parser.add_argument("--actions", type=str, default="../data/zork1.actions")
args = parser.parse_args()

printColor(f"building map: {args.map}, actions: {args.actions}", "b")
# prompt to confirm before continue
confirm = inputColor("Continue? (y/n) ", "b", inline=True)
if confirm == "y":
    g = build_graph_from_file(args.map, args.actions)
else:
    printColor("Aborted!", "b")
    exit(1)

plot_graph(g)

# generate pair-wise all paths between all nodes
# get generator of zip of any two different nodes from graph
all_pairs = list(itertools.combinations(g.nodes(), 2))
# print(all_pairs)

for srcNode, dstNode in all_pairs:
    shortest_paths = get_shortest_path(g, src=srcNode, dst=dstNode)
    print_path(g, shortest_paths, verbose=False)
