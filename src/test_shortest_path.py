import argparse
import itertools
import json

from digraph import (
    build_graph_from_file,
    build_graph_from_file_with_reverse,
    get_shortest_path,
    get_path_json,
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
        # prompt for src_node and dst_node, check if they exist in graph first
        while True:
            print("\033[92mWhere are you from? \033[0m")
            src_node = input().strip().lower()
            # check if src_node exist in graph
            if src_node not in g.nodes:
                print(f"[{src_node}] is not a valid location.")
                continue
            break

        while True:
            print("\033[92mWhere are you going? \033[0m")
            dst_node = input().strip().lower()
            # check if dst_node exist in graph
            if dst_node not in g.nodes:
                print(f"[{dst_node}] is not a valid location.")
                continue
            break

        # shortest path test
        shortest_path = get_shortest_path(g, src=src_node, dst=dst_node)
        shortest_path_json = get_path_json(g, shortest_path)

        # TODO: use dumped json to print only the actions
        with open("shortest.json", "w") as f:
            json.dump(shortest_path_json, f, indent=4)