import argparse
import itertools

from digraph import build_graph_from_file, get_all_paths, plot_graph, print_all_paths
from utils import inputColor, printColor

parser = argparse.ArgumentParser()
parser.add_argument("--map", "-m", type=str, default="../data/zork1.map")
parser.add_argument("--actions", "-a", type=str, default="../data/zork1.actions")
parser.add_argument("--output_dir", "-odir", type=str, default="../data/")
args = parser.parse_args()
args.output_path = (
    args.output_dir + args.map.split("/")[-1].split(".")[0] + ".all2all_paths.md"
)

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

f = open(args.output_path, "w")

for srcNode, dstNode in all_pairs:
    allPaths = get_all_paths(g, src=srcNode, dst=dstNode)
    path_string = print_all_paths(g, allPaths, verbose=False, diff_shortest=True)
    f.write(path_string)

f.close()
