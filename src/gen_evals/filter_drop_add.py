# this function serves to filter drop and add instances in inference results

import argparse
import json

import os
import sys

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from gen_paths.utils import compute_hash, compare_path_details
from gen_paths.digraph import anno_to_code

MAP_DIR = "./data/maps"
# INFER_DIR = "../gpt-games-results"
INFER_DIR = "../mango-inhouse-llms/llama"
DIFF_DIR = "./data/maps-diff-fjd"
DIFF_RESULT_DIR = "outputs_diff"

parser = argparse.ArgumentParser()
parser.add_argument("--tgt_game", "-t", type=str, default="anchor")
args = parser.parse_args()

TGT_GAME = args.tgt_game

# get all available games in infered result dir, ignore hidden files and hidden dirs and non-dir files
games = [
    f
    for f in os.listdir(INFER_DIR)
    if os.path.isdir(os.path.join(INFER_DIR, f)) and not f.startswith(".")
]
# exclude "outputs_diff"
games = [f for f in games if f != DIFF_RESULT_DIR]
print(len(games))


# get all available games in diff dir
games_diff = [
    f for f in os.listdir(DIFF_DIR) if os.path.isdir(os.path.join(DIFF_DIR, f))
]
print(len(games_diff))


# # get all available games in outputs_diff dir
# games_diff_result = [
#     f
#     for f in os.listdir(os.path.join(INFER_DIR, DIFF_RESULT_DIR))
#     if os.path.isdir(os.path.join(INFER_DIR, DIFF_RESULT_DIR, f))
# ]
# print(len(games_diff_result))


# each game_diff has two files: a "game.all2all.drop.json", a "game.all2all.new.json"
# use drop.json to filter out drop instances in infered result
# use new.json to filter out add instances in outputs_diff

# ================ DROP =================
for game in sorted(games_diff):
    if TGT_GAME is not None and game != TGT_GAME:
        continue

    print(f"===== check & drop [{game}] =====")
    diff_files_path = os.path.join(DIFF_DIR, game)
    drop_json_path = os.path.join(diff_files_path, f"{game}.all2all.drop.json")
    anno2code_path = os.path.join(MAP_DIR, game, f"{game}.anno2code.json")

    # if drop_json_path not exist, then there is nothing to drop
    if not os.path.exists(drop_json_path):
        continue

    # load anno2code dict
    with open(anno2code_path, "r") as f:
        anno2code = json.load(f)

    # load such drop_dict
    with open(drop_json_path, "r") as f:
        drop_dict = json.load(f)
    print(f"game: {game}, drop_dict len: {len(drop_dict)}")

    # take care of new_only_diff_shortest.json
    new_only_diff_shortest_json_path = os.path.join(
        diff_files_path, f"{game}.all2all.new_only_diff_shortest.json"
    )
    new_only_diff_shortest_dict = []
    if os.path.exists(new_only_diff_shortest_json_path):
        with open(new_only_diff_shortest_json_path, "r") as f:
            new_only_diff_shortest_dict = json.load(f)
        print(
            f"game: {game}, new_only_diff_shortest_dict len: {len(new_only_diff_shortest_dict)}"
        )

    # compute hash for this json

    # get all infered results for game
    infered_files_path = os.path.join(INFER_DIR, game, "results")
    # only "stepnav" subfolders needs to be checked for drop
    # stepnav_gpt35 = os.path.join(infered_files_path, "stepnav-gpt-3.5-turbo")
    # stepnav_gpt4 = os.path.join(infered_files_path, "stepnav-gpt-4")
    stepnav_gpt35 = os.path.join(infered_files_path, "stepnav_llama")
    stepnav_gpt4 = os.path.join(infered_files_path, "stepnav_llama_anno")

    print(f"stepnav_gpt35: {len(os.listdir(stepnav_gpt35))}")
    print(f"stepnav_gpt4: {len(os.listdir(stepnav_gpt4))}")

    # get list of all file paths in stepnav_gpt35 and stepnav_gpt4
    stepnav_gpt35_files = [
        os.path.join(stepnav_gpt35, f)
        for f in os.listdir(stepnav_gpt35)
        if not f.endswith("dropped.json")
    ]
    stepnav_gpt4_files = [
        os.path.join(stepnav_gpt4, f)
        for f in os.listdir(stepnav_gpt4)
        if not f.endswith("dropped.json")
    ]
    # sort stepnav_gpt35_files and stepnav_gpt4_files by file name, some of them has timestamp, newer comes first
    # stepnav_gpt35_files = sorted(stepnav_gpt35_files, key=lambda x: x.split("/")[-1])
    stepnav_gpt4_files = sorted(
        stepnav_gpt4_files, key=lambda x: x.split("/")[-1], reverse=True
    )
    stepnav_gpt4_files = sorted(
        stepnav_gpt4_files, key=lambda x: x.split("/")[-1], reverse=True
    )

    stepnav_all_files = stepnav_gpt35_files + stepnav_gpt4_files

    counter = 0
    # go over each files in stepnav_gpt35, load json
    for gpt_result_path in stepnav_all_files:
        with open(gpt_result_path, "r") as f:
            gpt_result = json.load(f)
        # find matching entries in drop_dict with same src_node, and dst_node
        src_node = gpt_result["src_node"]
        src_code = anno_to_code(src_node, anno2code)
        dst_node = gpt_result["dst_node"]
        dst_code = anno_to_code(dst_node, anno2code)

        # check if this result_json uses something in new_only_diff_shortest_dict
        # if so, skip this result_json but also remove this entry from new_only_diff_shortest_dict
        skip_once_flag = False
        coarse_matches_only_diff_shortest = []
        for obj in new_only_diff_shortest_dict:
            if (
                obj["src_node"] == src_code
                and obj["dst_node"] == dst_code
                and len(obj["path_details"]) == len(gpt_result["path_gt"])
                and compare_path_details(obj["path_details"], gpt_result["path_gt"])
            ):
                coarse_matches_only_diff_shortest.append(obj)
                print(f"coarse_matches_only_diff_shortest: +1")
                skip_once_flag = True
                break
        assert (
            len(coarse_matches_only_diff_shortest) <= 1
        ), "should be at most 1 match, for only_diff_shortest"
        if skip_once_flag:
            continue

        # iterate over drop_hash, test each obj's src and dst to find coarsely matching
        coarse_matches = []
        for obj in drop_dict:
            if (
                obj["src_node"] == src_code
                and obj["dst_node"] == dst_code
                and len(obj["path_details"]) == len(gpt_result["path_gt"])
            ):
                # rename this file with "dropped" extension
                coarse_matches.append(obj)
                # print(f"coarse match: +1")

        # compute hash using temp struct
        path_gt = gpt_result["path_gt"]
        # hash_code = compute_hash(path_gt, "path_details")
        # print(temp_struct)

        # check if it is in drop_dict
        for obj in coarse_matches:
            # coarse_match_hash = compute_hash(obj["path_details"], "path_details")
            # if hash_code == coarse_match_hash:
            if compare_path_details(obj["path_details"], path_gt):
                # rename this file with "dropped" extension
                # os.rename(gpt_result_path, gpt_result_path + ".dropped") when rerun this will introduce multiple .dropped. Fix it:
                gpt_result_path_new_name = gpt_result_path.replace(
                    ".json", ".dropped.json"
                )
                os.rename(gpt_result_path, gpt_result_path_new_name)
                print(f"dropped: {gpt_result_path}")
                counter += 1
                break
    print(f"dropped [{counter}] files")
    break
