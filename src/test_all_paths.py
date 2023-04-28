import argparse

from digraph import build_graph_from_file, get_all_paths, plot_graph, print_all_paths
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

    # all path test
    allPaths = get_all_paths(g, src=srcNode, dst=dstNode)
    print_all_paths(g, allPaths)
