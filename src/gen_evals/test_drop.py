import argparse
import json

import os
import sys

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from gen_paths.utils import compute_hash
from gen_paths.digraph import anno_to_code

MAP_DIR = "./data/maps"
# INFER_DIR = "../gpt-games-results"
INFER_DIR = "../mango-inhouse-llms/llama"
DIFF_DIR = "./data/maps-diff-fjd"
DIFF_RESULT_DIR = "outputs_diff"


parser = argparse.ArgumentParser()
parser.add_argument("--tgt_game", '-t', type=str, default="anchor")
args = parser.parse_args()

TGT_GAME = args.tgt_game

file_drop = f"./data/maps-diff-fjd/{TGT_GAME}/{TGT_GAME}.all2all.drop.json"
file_new = f"./data/maps-diff-fjd/{TGT_GAME}/{TGT_GAME}.all2all.new.json"

# load file
json_drop = json.load(open(file_drop, "r"))
json_new = json.load(open(file_new, "r"))


def compare_path_details(path1, path2):
    assert len(path1) == len(path2), f"len(path1)={len(path1)}, len(path2)={len(path2)}"

    for i in range(len(path1)):
        prev_node_1 = path1[i]["prev_node"]
        prev_node_2 = path2[i]["prev_node"]
        node_1 = path1[i]["node"]
        node_2 = path2[i]["node"]
        action_1 = path1[i]["action"]
        action_2 = path2[i]["action"]
        seen_1 = path1[i]["seen_in_forward"]
        seen_2 = path2[i]["seen"]
        if prev_node_1 != prev_node_2:
            return False
        if node_1 != node_2:
            return False
        if action_1 != action_2:
            return False
        if seen_1 != seen_2:
            return False

    return True


new_objects_not_only_diff_shortest = []
new_objects_only_diff_shortes = []
for each_new in json_new:
    src_new = each_new["src_node"]
    dst_new = each_new["dst_node"]
    diff_shortest_new = each_new["diff_shortest"]
    len_new = len(each_new["path_details"])

    for each_drop in json_drop:
        src_drop = each_drop["src_node"]
        dst_drop = each_drop["dst_node"]
        diff_shortest_drop = each_drop["diff_shortest"]
        len_drop = len(each_drop["path_details"])

        if src_new != src_drop or dst_new != dst_drop or len_new != len_drop:
            continue
        else:
            if compare_path_details(
                each_new["path_details"], each_drop["path_details"]
            ):
                print(f"found dropped path in new paths")
                if diff_shortest_new != diff_shortest_drop:
                    print(f"but diff_shortest is different")
                    new_objects_only_diff_shortes.append(each_new)
                else:
                    print(f"and diff_shortest is the same")
                    new_objects_not_only_diff_shortest.append(each_new)


print(f"new_objects_not_only_diff_shortest: {len(new_objects_not_only_diff_shortest)}")
print(f"new_objects_only_diff_shortes: {len(new_objects_only_diff_shortes)}")
