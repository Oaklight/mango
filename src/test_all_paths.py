import argparse
import itertools
import json

from digraph import (
    build_graph_from_file,
    build_graph_from_file_with_reverse,
    get_all_paths,
    get_all_paths_json,
    plot_graph,
)
from utils import confirm_continue, get_args_all2all

if __name__ == "__main__":
    args = get_args_all2all()
    confirm_continue()

    if args.reverse_map:
        g = build_graph_from_file_with_reverse(args.map, args.reverse_map)
    else:
        g = build_graph_from_file(args.map, args.actions)

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
        all_paths = get_all_paths(g, src=srcNode, dst=dstNode)
        all_paths_json = get_all_paths_json(g, all_paths, diff_shortest=True)
        
        # TODO: use dumped json to print only the actions
        with open("all2all.json", "w") as f:
            json.dump(all_paths_json, f, indent=4)
