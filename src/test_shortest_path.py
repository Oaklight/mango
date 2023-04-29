import argparse

from digraph import build_graph_from_file, get_shortest_path, plot_graph, print_path, build_graph_from_file_with_reverse
from utils import inputColor, printColor

parser = argparse.ArgumentParser()
parser.add_argument("--map", type=str, default="../data/zork1.map")
parser.add_argument("--actions", type=str, default="../data/zork1.actions")
parser.add_argument("--reverse_map", type=str, default="../data/zork1.map.reversed")
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

while True:
    # prompt for srcNode and dstNode, check if they exist in graph first
    while True:
        print("\033[92mWhere are you from? \033[0m")
        srcNode = input().strip().lower()
        # check if srcNode exist in graph
        if srcNode not in g.nodes:
            print(f"[{srcNode}] is not a valid location.")
            continue
        break

    while True:
        print("\033[92mWhere are you going? \033[0m")
        dstNode = input().strip().lower()
        # check if dstNode exist in graph
        if dstNode not in g.nodes:
            print(f"[{dstNode}] is not a valid location.")
            continue
        break

    # shortest path test
    shortestPath = get_shortest_path(g, src=srcNode, dst=dstNode)
    print_path(g, shortestPath)
