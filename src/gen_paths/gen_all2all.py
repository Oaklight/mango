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

    # generate pair-wise all paths between all nodes
    # get generator of zip of any two different nodes from graph
    all_pairs = list(itertools.combinations(g.nodes(), 2))
    # print(all_pairs)

    all_paths_json = []
    for src_node, dst_node in all_pairs:
        allPaths = get_all_paths(g, src=src_node, dst=dst_node)
        all_paths_json += get_all_paths_json(g, allPaths, diff_shortest=True)

    # if all_paths_json is empty, abort dumping
    if len(all_paths_json) == 0:
        print("No paths found. Abort dumping.")
        exit(2)

    # dump to json
    with open(args.output_path, "w") as f:
        json.dump(all_paths_json, f, indent=4)
