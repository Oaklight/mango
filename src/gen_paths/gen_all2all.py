import argparse
import itertools
import json
import os

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
    # this has some issue: AB or BA will be included, not both
    all_pairs = list(itertools.combinations(g.nodes(), 2))
    # this will include both AB and BA
    # all_pairs = list(itertools.permutations(g.nodes(), 2))
    # print(all_pairs)

    all_pairs_dict = {}
    all_paths_json = []
    for src_node, dst_node in all_pairs:
        print(f"Generating paths from {src_node} to {dst_node}...")
        allPaths = get_all_paths(g, src=src_node, dst=dst_node)
        all_paths_json += get_all_paths_json(g, allPaths, diff_shortest=True)

        all_pairs_dict[src_node + " -> " + dst_node] = {
            "src_node": src_node,
            "dst_node": dst_node,
            "num_paths": len(allPaths),
        }

    # sort by src, dst, diff_shortest, step_count
    # additionally sort by elements in path_details
    all_paths_json = sorted(
        all_paths_json,
        key=lambda x: (
            x["src_node"],
            x["dst_node"],
            x["diff_shortest"],
            x["step_count"],
            x["path_details"][0]["prev_node"],
            x["path_details"][0]["node"],
            x["path_details"][0]["action"],
        ),
    )

    # if all_paths_json is empty, abort dumping
    if len(all_paths_json) == 0:
        print("No paths found. Abort dumping.")
        exit(2)

    # dump to json
    with open(args.output_path, "w") as f:
        json.dump(all_paths_json, f, indent=4)

    # dump another file for all node pairs
    pair_json_path = os.path.join(
        os.path.dirname(args.output_path),
        args.map.split("/")[-1].split(".")[0] + ".all_pairs.json",
    )
    # sort by src, dst, num_paths
    all_pairs_dict = sorted(
        all_pairs_dict.items(),
        key=lambda x: (x[1]["src_node"], x[1]["dst_node"], x[1]["num_paths"]),
    )
    with open(pair_json_path, "w") as f:
        json.dump(all_pairs_dict, f, indent=4)
