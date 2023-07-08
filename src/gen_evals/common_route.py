import json
import os
import sys
import networkx as nx

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from gen_evals.utils import check_format, extract_actions
from gen_paths.gamegraph import anno_to_code, walk_path_to_dst, walk_and_label_path


def verify_pathgen_simple(g, anno2code, each_json_path, verbose=True):
    if verbose:
        print("verifying ", each_json_path)
    with open(each_json_path, "r") as f:
        gpt_results = json.load(f)

    src_anno = gpt_results["src_node"]
    dst_anno = gpt_results["dst_node"]
    dst_requested = anno_to_code(dst_anno, anno2code)
    src_requested = anno_to_code(src_anno, anno2code)

    path_gpt = []

    verify_result = False
    connectivity = nx.has_path(g, src_requested, dst_requested)

    verify_pack = {
        "verify_result": False,
        "src_anno": src_anno,
        "src_requested": src_requested,
        "dst_anno": dst_anno,
        "dst_requested": dst_requested,
        "connectivity": connectivity,
        "dist_shortest": nx.shortest_path_length(g, src_requested, dst_requested)
        if connectivity
        else None,
        "action_gpt": None,
        "dst_gpt": None,
        "verify_msg": "",
    }

    # check if each entry of path_gpt is in the correct format
    good_format, path_gpt = check_format(gpt_results)
    msg = "bad format" if not good_format else ""

    if good_format:
        if not connectivity and len(path_gpt) > 0:
            good_format = False
            msg = "no connectivity, yet path_gpt is not empty"

    if not good_format:
        if verbose:
            print("bad format: ", msg)

        verify_result = False
        verify_pack["verify_msg"] = msg
        return verify_result, verify_pack

    # extract action from path_gpt
    path_gpt_actions = [each["action"] for each in path_gpt]
    verify_pack["action_gpt"] = path_gpt_actions

    dst_gpt, msg = walk_path_to_dst(g, src_anno, path_gpt_actions, anno2code)

    if (
        dst_requested is None
        or dst_gpt is None
        or dst_gpt.lower() != dst_requested.lower()
    ):
        msg = f"wrong path, fail to arrive at dst: {dst_gpt}, {dst_requested}"
        if verbose:
            print(msg)
        verify_result = False
    else:
        if verbose:
            print("correct")
        verify_result = True

    verify_pack["verify_result"] = verify_result
    verify_pack["verify_msg"] = msg
    verify_pack["dst_gpt"] = dst_gpt

    return verify_result, verify_pack


def verify_pathgen_hard(g, anno2code, each_json_path, verbose=True):
    if verbose:
        print("verifying ", each_json_path)
    with open(each_json_path, "r") as f:
        gpt_results = json.load(f)

    src_anno = gpt_results["src_node"]
    dst_anno = gpt_results["dst_node"]
    dst_requested = anno_to_code(dst_anno, anno2code)
    src_requested = anno_to_code(src_anno, anno2code)

    path_gpt = []

    verify_result = False
    connectivity = nx.has_path(g, src_requested, dst_requested)

    verify_pack = {
        "verify_result": False,
        "src_anno": src_anno,
        "src_requested": src_requested,
        "dst_anno": dst_anno,
        "dst_requested": dst_requested,
        "connectivity": connectivity,
        "dist_shortest": nx.shortest_path_length(g, src_requested, dst_requested)
        if connectivity
        else None,
        "action_gpt": None,
        "dst_gpt": None,
        "verify_msg": "",
    }

    good_format, path_gpt = check_format(gpt_results)
    msg = "bad format" if not good_format else ""

    if good_format:
        if not connectivity and len(path_gpt) > 0:
            good_format = False
            msg = "no connectivity, yet path_gpt is not empty"

    if not good_format:
        if verbose:
            print("bad format: ", msg)

        verify_result = False
        verify_pack["verify_result"] = verify_result
        verify_pack["stop_node_code"] = None
        # -3 means bad format, -2 means empty path, -1 means bad src node, 0 means bad 1st prev_node.
        verify_pack["stop_step"] = -3
        verify_pack["path_checked"] = path_gpt
        verify_pack["verify_msg"] = msg

        return verify_result, verify_pack

    # extract action from path_gpt
    stop_node_code, stop_step, path_labeled, msg = walk_and_label_path(
        g, src_anno, path_gpt, anno2code
    )
    if msg == "all good":
        msg = "walk_and_label_path: the generated path leads to somewhere"
        print(msg)

        if stop_node_code == dst_requested:
            msg = "arrive at dst!"
            verify_result = True
        else:
            msg = "stop at somewhere else, not dst requested"
        print(msg)

        verify_pack["verify_result"] = verify_result
        verify_pack["stop_node_code"] = stop_node_code
        verify_pack["stop_step"] = stop_step
        verify_pack["path_checked"] = path_labeled
        verify_pack["verify_msg"] = msg
    else:
        verify_result = False
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
