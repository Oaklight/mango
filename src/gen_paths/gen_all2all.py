import itertools
import json
import os
import sys

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from gen_paths.digraph import (
    build_graph_from_file,
    build_graph_from_file_with_reverse,
    get_all_paths,
    get_all_paths_json,
    plot_graph,
)
from gen_paths.utils import confirm_continue, get_args_all2all


if __name__ == "__main__":
    args = get_args_all2all()
    confirm_continue()

    if args.reverse_map:
        g = build_graph_from_file_with_reverse(args.map, args.reverse_map)
    else:
        g = build_graph_from_file(args.map, args.actions)

    plot_graph(g)

    # load node_step_map
    node_step_map = None
    if args.node_step_map:
        with open(args.node_step_map, "r") as f:
            node_step_map = json.load(f)
            node_step_map = {k.lower(): int(v) for k, v in node_step_map.items()}

    # generate pair-wise all paths between all nodes
    # get generator of zip of any two different nodes from graph
    # this has some issue: AB or BA will be included, not both
    # all_pairs = list(itertools.combinations(g.nodes(), 2))
    # this will include both AB and BA
    all_pairs = list(itertools.permutations(g.nodes(), 2))
    # print(all_pairs)

    all_pairs_dict = []
    all_paths_json = []
    for src_node, dst_node in all_pairs:
        print(f"Generating paths from {src_node} to {dst_node}...")
        allPaths = get_all_paths(g, src=src_node, dst=dst_node)
        current_all_paths_json = get_all_paths_json(
            g, allPaths, diff_shortest=True, node_step_map=node_step_map
        )
        all_paths_json += current_all_paths_json

        all_pairs_dict.append(
            {
                "src_node": src_node,
                "dst_node": dst_node,
                "num_paths": len(allPaths),
                "path_min_cutoffs": [
                    path["path_min_cutoff"] for path in current_all_paths_json
                ],
            }
        )

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

    all_pairs_dict = sorted(
        all_pairs_dict,
        key=lambda x: (x["src_node"], x["dst_node"], x["num_paths"]),
    )

    with open(pair_json_path, "w") as f:
        json.dump(all_pairs_dict, f, indent=4)
