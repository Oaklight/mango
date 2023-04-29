import argparse

from digraph import build_graph_from_file, parse_path, plot_graph, verify_path, build_graph_from_file_with_reverse
from utils import inputColor, printColor

parser = argparse.ArgumentParser()
parser.add_argument("--map", type=str, default="../data/zork1.map")
parser.add_argument("--actions", type=str, default="../data/zork1.actions")
parser.add_argument("--reverse_map", '-r', type=str, default="../data/zork1.map.reversed")
args = parser.parse_args()
if args.actions == 'None' or args.actions == 'none' or args.actions == '':
    args.actions = None
if args.reverse_map == 'None' or args.reverse_map == 'none' or args.reverse_map == '':
    args.reverse_map = None

printColor(f"building map: {args.map}, actions: {args.actions}", "b")
# prompt to confirm before continue
confirm = inputColor("Continue? (y/n) ", "b", inline=True)
if confirm == "y":
    if args.reverse_map:
        g = build_graph_from_file_with_reverse(args.map, args.reverse_map, args.actions)
    else:
        g = build_graph_from_file(args.map, args.actions)
else:
    printColor("Aborted!", "b")
    exit(1)

plot_graph(g)

# verify path test
srcNode, dstNode, paths2verify = parse_path("../data/zork1.verify")
result = verify_path(g, srcNode, dstNode, paths2verify)
print(f"VERIFIED RESULT: \033[1m{result}\033[0m")
