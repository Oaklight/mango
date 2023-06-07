import glob
import json
import os
import sys

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from gen_evals.common_desti import verify_stepnav_hard, verify_stepnav_simple
from gen_evals.utils import (
    compute_json_uuid,
    parse_args,
    random_guess_rate,
    recompute_for_uuid,
    skip_due_to_cutoff,
)
from gen_paths.digraph import build_graph_from_file_with_reverse


if __name__ == "__main__":
    """
    this script serves to evaluate the destination finding task
    it loads game.map.human, game.map.reversed and build the map
    then it loads the gpt result file and check the destination it found
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

    # load cutoff info
    cutoff_json = args.cutoff_json
    with open(cutoff_json, "r") as f:
        cutoff_info = json.load(f)
        global_cutoff_step = int(cutoff_info[args.game])

    # load all_pairs.json
    all_pairs_json = os.path.join(args.tgt_path, f"{args.game}.all_pairs.json")
    with open(all_pairs_json, "r") as f:
        all_pairs = json.load(f)

    # load and build the map
    print(f"Loading map: [{args.game}]")
    map_human = os.path.join(args.tgt_path, f"{args.game}.map.human")
    map_reversed = os.path.join(args.tgt_path, f"{args.game}.map.reversed")
    g = build_graph_from_file_with_reverse(map_human, map_reversed, verbose=False)
    print(f"number of nodes: [{len(g.nodes)}]")
    print("\n\n\n\n\n")

    gpt_result_dir = args.gpt_result_dir
    gpt_prompt_version = ["stepnav_llama_anno"]
    random_guess_DF, _ = random_guess_rate(all2all, anno2code)
    verify_collections = {}

    for each_version in gpt_prompt_version:
        assert "stepnav" in each_version, "only destination finding task is supported"

        current_path = f"{gpt_result_dir}/{each_version}"
        gpt_result_jsons = glob.glob(f"{current_path}/*.json")
        gpt_result_jsons = [
            each_json
            for each_json in gpt_result_jsons
            if ".dropped.json" not in each_json
        ]

        correct = 0
        total = 0

        current_collection = {}
        for each_json in gpt_result_jsons:
            if args.verbose:
                print(f"Evaluating: [{each_json}]")

            micro_uuid = compute_json_uuid(each_json, level="micro")
            macro_uuid = compute_json_uuid(each_json, level="macro")

            # skip due to cutoff
            if skip_due_to_cutoff(
                "desti", each_json, global_cutoff_step, anno2code, all_pairs=all_pairs
            ):
                print(f"skip due to cutoff: [{each_json}]")
                continue

            if args.simple:
                verify_result, verify_pack = verify_stepnav_simple(
                    g, anno2code, each_json, args.verbose
                )
            else:
                verify_result, verify_pack = verify_stepnav_hard(
                    g, anno2code, each_json, args.verbose
                )

            print("got verified")
            if verify_result:
                correct += 1
            total += 1

            verify_pack["micro_uuid"] = micro_uuid
            verify_pack["macro_uuid"] = macro_uuid
            current_collection[each_json] = verify_pack

        random_guess = random_guess_DF
        verify_collections[each_version] = {
            "correct_num": correct,
            "total_num": total,
            "accuracy": correct / float(total) if total > 0 else 0,
            "collection": current_collection,
            "random_guess_rate": random_guess,
        }

        if args.simple:
            json_output = os.path.join(args.output_dir, "destination.nice.json")
        else:
            json_output = os.path.join(args.output_dir, "destination.harsh.json")
        with open(json_output, "w") as f:
            json.dump(verify_collections, f, indent=4)

        recompute_for_uuid(json_output)  # hash and deduplicate, then plot
        # rename all *_acc_vs_length.png to *_acc_vs_length.harsh.png

        version = "nice" if args.simple else "harsh"
        for each_png in glob.glob(f"{args.output_dir}/*_acc_vs_term_dist.png"):
            os.rename(each_png, each_png.replace(".png", f".{version}.png"))

        for each_png in glob.glob(f"{args.output_dir}/*_acc_vs_route_length.png"):
            os.rename(each_png, each_png.replace(".png", f".{version}.png"))

        for each_png in glob.glob(f"{args.output_dir}/*.png"):
            os.rename(each_png, each_png.replace("stepnav_llama_anno", "desti_finding"))
