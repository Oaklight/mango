import argparse
import itertools
import json

from digraph import (
    build_graph_from_file,
    get_shortest_path,
    plot_graph,
    build_graph_from_file_with_reverse,
    get_path_json,
)
from md2json import md2json
from utils import input_color, print_color

parser = argparse.ArgumentParser()
parser.add_argument("--map", "-m", type=str, default="../data/zork1.map")
parser.add_argument("--actions", "-a", type=str, default="../data/zork1.actions")
parser.add_argument(
    "--reverse_map", "-r", type=str, default="../data/zork1.map.reversed"
)
parser.add_argument("--output_dir", "-odir", type=str, default="../data/")
args = parser.parse_args()
args.output_path = (
    args.output_dir + args.map.split("/")[-1].split(".")[0] + ".all2all.shortest.json"
)
if args.actions == "None" or args.actions == "none" or args.actions == "":
    args.actions = None
if args.reverse_map == "None" or args.reverse_map == "none" or args.reverse_map == "":
    args.reverse_map = None

print_color(f"building map: {args.map}, actions: {args.actions}", "b")
# prompt to confirm before continue
confirm = input_color("Continue? (y/n) ", "b", inline=True)
if confirm == "y":
    if args.reverse_map:
        g = build_graph_from_file_with_reverse(args.map, args.reverse_map)
    else:
        g = build_graph_from_file(args.map, args.actions)
else:
    print_color("Aborted!", "b")
    exit(1)

plot_graph(g)

# generate pair-wise all paths between all nodes
# get generator of zip of any two different nodes from graph
all_pairs = list(itertools.combinations(g.nodes(), 2))
# print(all_pairs)


shortest_paths_json = []
for src_node, dst_node in all_pairs:
    shortest_paths = get_shortest_path(g, src=src_node, dst=dst_node)
    shortest_paths_json.append(get_path_json(g, shortest_paths))

# f = open(args.output_path, "w")
# dump to json
with open(args.output_path, "w") as f:
    json.dump(shortest_paths_json, f, indent=4)
