import json
import os
import sys
import networkx as nx

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from gen_evals.utils import check_format, extract_actions
from gen_paths.digraph import anno_to_code, walk_path_to_dst


def verify_stepnav_simple(anno2code, g, each_json_path, verbose=True):
    if verbose:
        print("verifying ", each_json_path)
    with open(each_json_path, "r") as f:
        gpt_results = json.load(f)

    src_requested = anno_to_code(gpt_results["src_node"], anno2code)
    dst_requested = anno_to_code(gpt_results["dst_node"], anno2code)
    # dst_requested, msg = walk_path_to_dst(g, src_anno, action_requested, anno2code)
    
    action_requested = extract_actions(gpt_results["question"])

    path_gpt = []

    # default values
    verify_result = False
    verify_pack = {
        "verify_result": verify_result,
        "src_requested": src_requested,
        "dst_requested": dst_requested,
        "action_requested": action_requested,
        "route_length": len(action_requested),
        "dist_shortest": nx.shortest_path_length(g, src_requested, dst_requested),
        "dst_gpt": None,  # to be changed
        "verify_msg": "",  # to be changed
    }

    # FIXME: no need to check format as long as it has useable dst node
    good_format, path_gpt = check_format(gpt_results, dst_only=True)
    msg = "bad format" if not good_format else ""

    if not good_format:
        verify_pack["verify_msg"] = msg
        return verify_result, verify_pack

    dst_gpt = anno_to_code(path_gpt[-1]["node"], anno2code)

    # check if the dst node is correct
    if (
        dst_requested is None
        or dst_gpt is None
        or dst_gpt.lower() != dst_requested.lower()
    ):
        if verbose:
            print("wrong dst node", dst_gpt, dst_requested)
        msg = "wrong dst node"
    else:
        if verbose:
            print("correct", dst_gpt, dst_requested)
        verify_result = True

    verify_pack["verify_result"] = verify_result
    verify_pack["verify_msg"] = msg
    verify_pack["dst_gpt"] = dst_gpt

    return verify_result, verify_pack
