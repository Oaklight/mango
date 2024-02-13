import argparse
import itertools
import json
import os
import sys

import networkx
from tqdm import tqdm

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from gen_paths.gamegraph import plot_graph
from gen_paths.utils import confirm_continue, generate_combinations, print_args

STEP_INF = 9999


def parse_edge(edge_str, reversed_detected=False):
    if reversed_detected:
        edge_str = edge_str.split(", desc:")[0]

    edge_str = edge_str.lower()

    edge_str, step_num = [x.strip() for x in edge_str.split(", step")]
    step_num, answerable_num = step_num.split(", answerable")
    src, act, dst = [x.strip() for x in edge_str.split("-->")]

    return ((src, act, dst), int(step_num), int(answerable_num))


def process_edges_from_map_file(path_file: str):
    """
    builds a graph from a csv file,
    - forward path: path (src_node --> action --> dst_node), step_num
    - backward path: path (dst_node --> opposite_action --> src_node), step_num, description
      if description is "None" this is a valid path, otherwise it's an invalid path
    """
    with open(path_file, "r") as f:
        lines = f.readlines()

    edges_to_add = {}
    if len(lines) == 0:
        return {}

    reversed_detected = "desc:" in lines[0]

    for line in lines:
        edge, step_num, answerable_num = parse_edge(line, reversed_detected)
        assert isinstance(answerable_num, int)
        if edge in edges_to_add:
            edges_to_add[edge]["step_num"].append(step_num)
            edges_to_add[edge]["answerable_num"].append(answerable_num)
        else:
            edges_to_add[edge] = {
                "step_num": [step_num],
                "answerable_num": [answerable_num],
            }

    return edges_to_add


def build_graph_from_file_with_reverse(
    human_file: str,
    reverse_file: str,
) -> object:
    """
    build map graph based on forward map (human_file) and reverse map (reverse_file)
    """
    # reverse map should have less or equal number of edges than forward map
    # each matching entry of reverse map should have the same set of nodes as its counterpart in forward map

    # load forward and reverse map file and count its number of lines
    with open(human_file, "r") as f:
        lines_forward = f.readlines()
    with open(reverse_file, "r") as f:
        lines_reverse = f.readlines()
    num_lines_forward = len(lines_forward)
    num_lines_reverse = len(lines_reverse)
    assert (
        num_lines_reverse <= num_lines_forward
    ), "reverse map should have less or equal number of edges than forward map"

    edges_forward_dict = process_edges_from_map_file(human_file)
    edges_reversed_dict = process_edges_from_map_file(reverse_file)

    # merge edges_forward_dict and edges_reversed_dict and update see_in_forward and see_in_backward
    edges_all = {}
    for edge, step_nums in edges_forward_dict.items():
        edges_all[edge] = {
            "seen_in_forward": min(step_nums["step_num"]),
            "seen_in_reversed": STEP_INF,
            "seen_in_forward_answerable": min(step_nums["answerable_num"]),
            "seen_in_reversed_answerable": STEP_INF,
        }
    for edge, step_nums in edges_reversed_dict.items():
        if edge not in edges_all:
            edges_all[edge] = {
                "seen_in_forward": STEP_INF,
                "seen_in_reversed": min(step_nums["step_num"]),
                "seen_in_forward_answerable": STEP_INF,
                "seen_in_reversed_answerable": min(step_nums["answerable_num"]),
            }
        else:
            edges_all[edge]["seen_in_reversed"] = min(
                edges_all[edge]["seen_in_reversed"], *step_nums["step_num"]
            )
            edges_all[edge]["seen_in_reversed_answerable"] = min(
                edges_all[edge]["seen_in_reversed_answerable"],
                *step_nums["answerable_num"],
            )

    # use MultiDiGraph instead to accomodate special game with multiple valid action between two nodes
    G = networkx.MultiDiGraph()

    for edge, attrs in edges_all.items():
        src, act, dst = edge
        attrs["action"] = act
        G.add_edge(src, dst, **attrs)

    return G


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", "-odir", type=str, required=True)
    parser.add_argument("--game", "-g", type=str, required=True)
    parser.add_argument("--no_confirm", "-nc", action="store_true")
    args = parser.parse_args()

    assert os.path.exists(
        args.output_dir
    ), f"output directory {args.output_dir} does not exist"

    args.human_map = os.path.join(args.output_dir, args.game, f"{args.game}.map.human")
    args.reverse_map = os.path.join(
        args.output_dir, args.game, f"{args.game}.map.reversed"
    )
    assert os.path.exists(args.human_map), f"map file {args.human_map} does not exist"
    assert os.path.exists(
        args.reverse_map
    ), f"reverse map file {args.reverse_map} does not exist"

    args.all2all = os.path.join(args.output_dir, args.game, f"{args.game}.all2all.json")
    args.allpairs = os.path.join(
        args.output_dir, args.game, f"{args.game}.all_pairs.json"
    )

    args.edges = os.path.join(args.output_dir, args.game, f"{args.game}.edges.json")
    args.nodes = os.path.join(args.output_dir, args.game, f"{args.game}.nodes.json")

    print_args(args)
    return args


def get_all_paths(G: object, src: str, dst: str):
    """
    get all paths from src to dst in MultiDiGraph
    then format the path to a list of quaduples (src, dst, direction, step_num)
    """
    expanded_simple_paths = []

    try:
        simple_paths = networkx.all_simple_paths(G, src, dst)
        simple_paths = list(set([tuple(path) for path in simple_paths]))
        simple_paths.sort(key=lambda x: len(x))

        for path in simple_paths:
            expanded_path = []
            for i in range(len(path) - 1):
                # get all variants of edges between path[i] and path[i+1]
                src = path[i]
                dst = path[i + 1]
                all_edges_btw_attrs = G.get_edge_data(src, dst)
                all_edges_btw = [
                    (src, dst, data) for data in all_edges_btw_attrs.values()
                ]

                expanded_path = generate_combinations(expanded_path, all_edges_btw)
            expanded_simple_paths.extend(expanded_path)

        return expanded_simple_paths

    except networkx.exception.NetworkXNoPath:
        return expanded_simple_paths


def get_all_paths_json(G, all_paths, diff_shortest=False):
    """
    iterate over all paths and print each
    all_paths is the expanded simple paths. Outter most list the collection of simple paths. Inner lists are lists of edge quadruplets (src_node, dst_node, direction, step_num)
    """
    path_json_list = []
    if len(all_paths) == 0:
        print("no path found")
        return path_json_list

    # sort all_paths by len of each
    all_paths = sorted(all_paths, key=lambda x: len(x))
    shortest_len = len(all_paths[0])

    for path in all_paths:
        if diff_shortest:
            path_json = get_path_json(G, path, shortest_length=shortest_len)
        else:
            path_json = get_path_json(G, path)
        path_json_list.append(path_json)

    return path_json_list


def get_path_json(g, path, shortest_length=None):
    """
    return path json
    path is a list of quadruplets (prev_node, node, action, step_num)
    """
    # get src_node and dst_node and print them
    src_node = path[0][0]
    dst_node = path[-1][1]

    path_json = {"src_node": src_node, "dst_node": dst_node}
    if shortest_length:
        diff_shortest = len(path) - shortest_length
        path_json["diff_shortest"] = diff_shortest

    path_details = []
    if len(path) == 0:
        pass
    else:
        for edge in path:
            prev_node, node, attrs = edge

            # use dict instead
            entry = {
                "prev_node": prev_node,
                "node": node,
                "action": attrs["action"],
                "seen_in_forward": attrs["seen_in_forward"],
                "seen_in_reversed": attrs["seen_in_reversed"],
                "edge_min_step": min(
                    attrs["seen_in_forward"], attrs["seen_in_reversed"]
                ),
                "seen_in_forward_answerable": attrs["seen_in_forward_answerable"],
                "seen_in_reversed_answerable": attrs["seen_in_reversed_answerable"],
                "edge_min_step_answerable": min(
                    attrs["seen_in_forward_answerable"],
                    attrs["seen_in_reversed_answerable"],
                ),
            }
            path_details.append(entry)

    path_json["path_details"] = path_details
    path_json["step_count"] = len(path_details)

    # the minimum step_num to see all the edges in map.human
    path_json["path_seen_in_forward"] = max(
        [each["seen_in_forward"] for each in path_details]
    )
    path_json["path_seen_in_forward_answerable"] = max(
        [each["seen_in_forward_answerable"] for each in path_details]
    )

    # the minimum step_num to see all the edges in either map.human or map.reversed
    path_json["path_min_step"] = max([each["edge_min_step"] for each in path_details])
    path_json["path_min_step_answerable"] = max(
        [each["edge_min_step_answerable"] for each in path_details]
    )

    return path_json


if __name__ == "__main__":
    args = parse_args()

    if args.no_confirm is False:
        confirm_continue()

    G = build_graph_from_file_with_reverse(args.human_map, args.reverse_map)
    print(f"NUM(G.node) = {len(G.nodes())}")
    print(f"NUM(G.edges) = {len(G.edges())}")

    g_edges = []
    for src, dst, attrs in G.edges(data=True):
        # print(attrs)
        g_edges.append(
            {
                "src_node": src,
                "dst_node": dst,
                "action": attrs["action"],
                "seen_in_forward": attrs["seen_in_forward"],
                "seen_in_reversed": attrs["seen_in_reversed"],
                "edge_min_step": min(
                    attrs["seen_in_forward"], attrs["seen_in_reversed"]
                ),
                "seen_in_forward_answerable": attrs["seen_in_forward_answerable"],
                "seen_in_reversed_answerable": attrs["seen_in_reversed_answerable"],
                "edge_min_step_answerable": min(
                    attrs["seen_in_forward_answerable"],
                    attrs["seen_in_reversed_answerable"],
                ),
            }
        )
    g_nodes = list(G.nodes())
    with open(args.edges, "w") as f:
        json.dump(g_edges, f, indent=4)
    with open(args.nodes, "w") as f:
        json.dump(g_nodes, f, indent=4)

    # plot_graph(G)

    # generate pair-wise all paths between all nodes
    # get generator of zip of any two different nodes from graph
    # this has some issue: AB or BA will be included, not both
    # all_pairs = list(itertools.combinations(g.nodes(), 2))
    # this will include both AB and BA
    all_pairs = list(itertools.permutations(G.nodes(), 2))
    # print(all_pairs)

    f_all2all = open(args.all2all, "w")
    f_allpairs = open(args.allpairs, "w")

    for src_node, dst_node in tqdm(all_pairs):
        print(f"Generating paths from {src_node} to {dst_node}...")

        # simple_paths of MultiDiGraph is still a list of list of nodes
        # but we want it to be a list of quadruples (src, dst, direction, step_num)
        # so we need to expand the simple_paths
        expanded_simple_paths = get_all_paths(G, src=src_node, dst=dst_node)

        current_all_paths_json = get_all_paths_json(
            G, expanded_simple_paths, diff_shortest=True
        )
        # all_paths_json += current_all_paths_json
        current_all_pairs_json = {
            "src_node": src_node,
            "dst_node": dst_node,
            "num_paths": len(expanded_simple_paths),
            "path_min_steps": [
                path["path_min_step"] for path in current_all_paths_json
            ],
            "path_seen_in_forward": [
                path["path_seen_in_forward"] for path in current_all_paths_json
            ],
            "path_seen_in_forward_answerable": [
                path["path_seen_in_forward_answerable"]
                for path in current_all_paths_json
            ],
        }
        # all_pairs_dict.append(current_all_pairs_json)
        for each in current_all_paths_json:
            f_all2all.write(json.dumps(each))
            f_all2all.write("\n")
        f_allpairs.write(json.dumps(current_all_pairs_json))
        f_allpairs.write("\n")

    f_all2all.close()
    f_allpairs.close()
