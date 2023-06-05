import argparse
import glob
import json
import math
import os
import sys
import uuid

import networkx as nx
import numpy as np
from matplotlib import pyplot as plt

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from gen_evals.common_route import verify_pathgen_simple, verify_pathgen_hard
from gen_evals.utils import (
    compute_json_uuid,
    parse_args,
    random_guess_rate,
    recompute_for_uuid,
)
from gen_paths.digraph import (
    build_graph_from_file_with_reverse,
)


if __name__ == "__main__":
    """
    this script serves to evaluate the route finding task
    it loads game.map.human and game.map.reversed and build the map
    then it loads the gpt result file and walk the route it found
    """
    args = parse_args()

    # this file contains the groundtruth of the destination finding task
    all2all_json = os.path.join(args.tgt_path, f"{args.game}.all2all.json")
    with open(all2all_json, "r") as f:
        all2all = json.load(f)

    # load and lower both key and values in code2anno and anno2code
    anno2code_json = os.path.join(args.tgt_path, f"{args.game}.anno2code.json")
    code2anno_json = os.path.join(args.tgt_path, f"{args.game}.code2anno.json")
    with open(anno2code_json, "r") as f:
        anno2code = json.load(f)
        anno2code = {k.lower(): v for k, v in anno2code.items()}
    with open(code2anno_json, "r") as f:
        code2anno = json.load(f)
        code2anno = {k.lower(): v for k, v in code2anno.items()}

    # load and build the map
    print(f"Loading map: [{args.game}]")
    map_human = os.path.join(args.tgt_path, f"{args.game}.map.human")
    map_reversed = os.path.join(args.tgt_path, f"{args.game}.map.reversed")
    g = build_graph_from_file_with_reverse(map_human, map_reversed, verbose=False)
    print(f"number of nodes: [{len(g.nodes)}]")
    print("\n\n\n\n\n")

    gpt_result_dir = args.gpt_result_dir
    gpt_prompt_version = [
        # "pathgen-gpt-3.5-turbo/",
        "pathgen-gpt-4/",
        # "stepnav-gpt-3.5-turbo/",
        # "stepnav-gpt-4/",
    ]
    _, random_guess_RF = random_guess_rate(all2all, anno2code)
    verify_collections = {}

    for each_version in gpt_prompt_version:
        assert "pathgen" in each_version, "only route finding task is supported"

        current_path = f"{gpt_result_dir}/{each_version}"
        gpt_result_jsons = glob.glob(f"{current_path}/*.json")

        correct = 0
        total = 0

        current_collection = {}
        for each_json in gpt_result_jsons:
            if args.verbose:
                print(f"Evaluating: [{each_json}]")

            micro_uuid = compute_json_uuid(each_json, level="micro")
            macro_uuid = compute_json_uuid(each_json, level="macro")

            if args.simple:
                verify_result, verify_pack = verify_pathgen_simple(
                    g, anno2code, each_json, args.verbose
                )
            else:
                verify_result, verify_pack = verify_pathgen_hard(
                    g, anno2code, each_json, args.verbose
                )

            if verify_result:
                correct += 1
            total += 1

            verify_pack["micro_uuid"] = micro_uuid
            verify_pack["macro_uuid"] = macro_uuid
            current_collection[each_json] = verify_pack

        random_guess = random_guess_RF
        verify_collections[each_version] = {
            "correct_num": correct,
            "total_num": total,
            "accuracy": correct / float(total),
            "collection": current_collection,
            "random_guess_rate": random_guess,
        }

        if args.simple:
            json_output = os.path.join(args.output_dir, "route.nice.json")
        else:
            json_output = os.path.join(args.output_dir, "route.harsh.json")
        with open(json_output, "w") as f:
            json.dump(verify_collections, f, indent=4)

        recompute_for_uuid(json_output)  # hash and deduplicate, then plot
        # rename all *_acc_vs_length.png to *_acc_vs_length.harsh.png

        version = "nice" if args.simple else "harsh"
        for each_png in glob.glob(f"{args.output_dir}/*_acc_vs_term_dist.png"):
            os.rename(each_png, each_png.replace(".png", f".{version}.png"))

        for each_png in glob.glob(f"{args.output_dir}/*.png"):
            os.rename(each_png, each_png.replace("pathgen-gpt-4", "route_finding"))