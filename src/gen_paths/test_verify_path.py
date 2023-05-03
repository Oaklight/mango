import argparse
import itertools
import json

from digraph import build_graph_from_file, parse_path, plot_graph, verify_path, build_graph_from_file_with_reverse
from utils import confirm_continue, get_args_all2all

if __name__ == "__main__":
    args = get_args_all2all()
    confirm_continue()

    if args.reverse_map:
        g = build_graph_from_file_with_reverse(args.map, args.reverse_map)
    else:
        g = build_graph_from_file(args.map, args.actions)

    plot_graph(g)

    # verify path test
    src_node, dst_node, paths2verify = parse_path("../data/zork1.verify")
    result = verify_path(g, src_node, dst_node, paths2verify)
    print(f"VERIFIED RESULT: \033[1m{result}\033[0m")
