import json
import os
import sys
import networkx as nx

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from gen_evals.utils import check_format, extract_actions
from gen_paths.digraph import anno_to_code, walk_path_to_dst, walk_and_label_path


def verify_stepnav_simple(g, anno2code, each_json_path, verbose=True):
    if verbose:
        print("verifying ", each_json_path)
    with open(each_json_path, "r") as f:
        gpt_results = json.load(f)

    src_requested = anno_to_code(gpt_results["src_node"], anno2code)
    dst_requested = anno_to_code(gpt_results["dst_node"], anno2code)
    # dst_requested, msg = walk_path_to_dst(g, src_anno, action_requested, anno2code)

    action_requested = gpt_results["action_list"]

    path_gpt = []

    # default values
    verify_result = False
    verify_pack = {
        "verify_result": False,
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

    if good_format:
        if len(action_requested) != 0 and len(path_gpt) == 0:
            good_format = False
            msg = "empty path_gpt when action_requested is not empty"
            if verbose:
                print("bad format: ", msg)

        elif path_gpt[-1]["node"] is None:
            good_format = False
            msg = "bad format: dst node is None"
            if verbose:
                print("bad format: ", msg)

    if not good_format:
        if verbose:
            print("bad format: ", msg)

        verify_pack["verify_msg"] = msg
        return verify_result, verify_pack

    dst_gpt = anno_to_code(path_gpt[-1]["node"], anno2code)

    # check if the dst node is correct
    if (
        dst_requested is None
        or dst_gpt is None
        or dst_gpt.lower() != dst_requested.lower()
    ):
        msg = f"wrong dst node {dst_gpt} {dst_requested}"
        if verbose:
            print(msg)
    else:
        if verbose:
            print("correct", dst_gpt, dst_requested)
        verify_result = True

    verify_pack["verify_result"] = verify_result
    verify_pack["verify_msg"] = msg
    verify_pack["dst_gpt"] = dst_gpt

    return verify_result, verify_pack


def verify_stepnav_hard(g, anno2code, each_json_path, verbose=True):
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
        "verify_result": False,
        "src_requested": src_requested,
        "dst_requested": dst_requested,
        "action_requested": action_requested,
        "route_length": len(action_requested),
        "dist_shortest": nx.shortest_path_length(g, src_requested, dst_requested),
        "dst_gpt": None,  # to be changed
        "verify_msg": "",  # to be changed
    }

    # check if each entry of path_gpt is in the correct format
    good_format, path_gpt = check_format(gpt_results)
    msg = "bad format" if not good_format else ""

    # check if each entry's action is following the requested action
    if good_format:
        for each_step in path_gpt:
            if each_step["action"] not in action_requested:
                good_format = False
                msg = f"wrong action, at step {each_step['action']}, aborting"
                break

    if not good_format:
        if verbose:
            print("bad format: ", msg)

        verify_pack["verify_msg"] = msg

        verify_result = False
        verify_pack["verify_result"] = verify_result
        verify_pack["stop_node_code"] = None
        # -3 means bad format, -2 means empty path, -1 means bad src node, 0 means bad 1st prev_node.
        verify_pack["stop_step"] = -3
        verify_pack["path_checked"] = path_gpt
        verify_pack["verify_msg"] = msg

        return verify_result, verify_pack

    # dst_gpt = anno_to_code(path_gpt[-1]["node"], anno2code)
    stop_node_code, stop_step, path_labeled, msg = walk_and_label_path(
        g, gpt_results["src_node"], path_gpt, anno2code
    )
    if msg == "all good":
        msg = "walk_and_label_path: the generated path leads to somewhere"
        print(msg)

        if stop_node_code == dst_requested:
            verify_result = True
            msg = "arrive at dst!"
        else:
            msg = "stop at somewhere else, not dst requested"
        print(msg)

        verify_pack["verify_result"] = verify_result
        verify_pack["stop_node_code"] = stop_node_code
        verify_pack["stop_step"] = stop_step
        verify_pack["path_checked"] = path_labeled
        verify_pack["verify_msg"] = msg

    if verify_result:
        assert (
            stop_node_code == dst_requested
        ), f"stop node is not the dst node SOMETHING IS WRONG IN WALKING_AND_LABEL_PATH: [{stop_node_code}] != [{dst_requested}]"

    return verify_result, verify_pack
