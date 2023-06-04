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

from gen_paths.digraph import (
    PathCheck,
    anno_to_code,
    build_graph_from_file_with_reverse,
    walk_and_label_path,
    walk_path_to_dst,
)

# # FIXME: use name exactly as in provided files, for example use "the troll room" instead of "troll room"
# def str_txt)
#     if str_txt == "troll room":
#         return "the troll room"
#     return str_txt

# there might be repeated tests, use latest results?
visited_jsons = {}


def compute_json_uuid(gpt_json, level="micro"):
    with open(gpt_json, "r") as f:
        gpt_json_dict = json.load(f)
    # compute a hash for the json dict
    # use the src and dst node as the hash
    src_node = gpt_json_dict["src_node"]
    dst_node = gpt_json_dict["dst_node"]
    task = gpt_json_dict["task"]
    path_gt = gpt_json_dict["path_gt"]
    question = gpt_json_dict["question"]
    if level == "micro":
        str_pack = f"{src_node}_{dst_node}_{task}_{path_gt}_{question}"
    elif level == "macro":
        str_pack = f"{src_node}_{dst_node}_{task}_{question}"
    else:
        raise ValueError(f"level {level} not supported")
    uuid_value = uuid.uuid3(uuid.NAMESPACE_DNS, str_pack)
    return str(uuid_value)


def load_all_jsons(json_dir):
    # get a list of all files in the directory using glob
    gpt_result_jsons = glob.glob(os.path.join(json_dir, "*.json"))
    for each_json_path in gpt_result_jsons:
        __load_json(each_json_path)
    print(f"loaded {len(visited_jsons)} jsons")


def __load_json(json_file):
    with open(json_file, "r") as f:
        json_loaded = json.load(f)
    # name of jsonfile has a timestamp: "results_2023-05-13-03-22-51_393.json"
    timestamp = json_file.split("_")[1].split(".")[0]
    rand_num = json_file.split("_")[2].split(".")[0]

    # if the json file has been visited before, check if the new one is newer
    # and put older one in "history" field, if current one is older than the existing one, directly add it to "history"
    # if not, add it to visited_jsons
    if json_file in visited_jsons:
        if visited_jsons[json_file]["timestamp"] < timestamp:
            tmp_json = visited_jsons[json_file]
            visited_jsons[json_file] = {
                "timestamp": timestamp,
                "rand_num": rand_num,
                "json_loaded": json_loaded,
                "history": [],
            }
            # move all history to the new one
            for each in tmp_json["history"]:
                visited_jsons[json_file]["history"].append(each)
            # add the old one to history
            tmp_json.pop("history")
            visited_jsons[json_file]["history"].append(tmp_json)
            # sort the history by timestamp
            visited_jsons[json_file]["history"].sort(
                key=lambda x: x["timestamp"], reverse=True
            )
        else:
            visited_jsons[json_file]["history"].append(
                {
                    "timestamp": timestamp,
                    "rand_num": rand_num,
                    "json_loaded": json_loaded,
                }
            )
    else:
        visited_jsons[json_file] = {
            "timestamp": timestamp,
            "rand_num": rand_num,
            "json_loaded": json_loaded,
            "history": [],
        }


def verify_pathgen_simple(g, anno2code, each_json_path):
    print("verifying ", each_json_path)
    with open(each_json_path, "r") as f:
        gpt_results = json.load(f)

    src_anno = gpt_results["src_node"]
    dst_anno = gpt_results["dst_node"]
    dst_requested = anno_to_code(dst_anno, anno2code)
    src_requested = anno_to_code(src_anno, anno2code)
    path_gpt = []

    # check if each entry of path_gpt is in the correct format
    good_format, path_gpt = check_format(gpt_results)
    msg = "bad format" if not good_format else ""

    if not good_format:
        print("bad format")
        verify_result = False
        return verify_result, {
            "verify_result": verify_result,
            "src_anno": src_anno,
            "dst_anno": dst_anno,
            "dist_shortest": nx.shortest_path_length(g, src_requested, dst_requested),
            "action_gpt": None,
            "dst_gpt": None,
            "dst_requested": dst_requested,
            "verify_msg": msg,
        }

    # extract action from path_gpt
    path_gpt_actions = [each["action"] for each in path_gpt]
    dst_gpt, msg = walk_path_to_dst(g, src_anno, path_gpt_actions, anno2code)

    if (
        dst_requested is None
        or dst_gpt is None
        or dst_gpt.lower() != dst_requested.lower()
    ):
        print("wrong path, fail to arrive at dst", dst_gpt, dst_requested)
        verify_result = False
    else:
        print("correct")
        verify_result = True
    return verify_result, {
        "verify_result": verify_result,
        "src_anno": src_anno,
        "dst_anno": dst_anno,
        "dist_shortest": nx.shortest_path_length(g, src_requested, dst_requested),
        "action_gpt": path_gpt_actions,
        "dst_gpt": dst_gpt,
        "dst_requested": dst_requested,
        "verify_msg": msg,
    }


def verify_pathgen(g, anno2code, each_json_path):
    print("verifying ", each_json_path)
    with open(each_json_path, "r") as f:
        gpt_results = json.load(f)

    src_anno = gpt_results["src_node"]
    dst_anno = gpt_results["dst_node"]
    path_gpt = []

    # check if each entry of path_gpt is in the correct format
    good_format, path_gpt = check_format(gpt_results)
    msg = "bad format" if not good_format else ""

    verify_result = False
    if good_format:
        stop_node_code, stop_step, path_labeled, msg = walk_and_label_path(
            g, src_anno, path_gpt, anno2code
        )
        if msg == "all good":
            # check if the dst node is correct
            if code2anno[stop_node_code].lower() == dst_anno.lower():
                print("correct")
                verify_result = True
            else:
                print("wrong dst node", code2anno[stop_node_code], dst_anno)
                verify_result = False
        print()

        verify_pack = {
            "verify_result": verify_result,
            "src_anno": src_anno,
            "dst_anno": dst_anno,
            "stop_step": stop_step,
            "stop_node_code": stop_node_code,
            "verify_msg": msg,
            "path_checked": path_labeled,
        }
    else:
        verify_pack = {
            "verify_result": verify_result,
            "src_anno": src_anno,
            "dst_anno": dst_anno,
            "stop_step": -3,
            "stop_node_code": None,
            "verify_msg": "bad format",
            "path_checked": gpt_results["path"],
        }
    return verify_result, verify_pack


def check_format(gpt_results):
    good_format = True
    path_gpt = []
    if "path" not in gpt_results:
        good_format = False
        return good_format, path_gpt

    for i, each in enumerate(gpt_results["path"]):
        if isinstance(each, dict):
            # check if it has the correct keys
            if "prev_node" in each and "node" in each and "action" in each:
                # check if action is null, if null, drop it and everything after it
                # except for the beginning and end one, skip these two if they are null
                # otherwise, the format is bad
                if each["action"] is None:
                    if i == 0 or i == len(gpt_results["path"]) - 1:
                        continue
                    else:
                        good_format = False
                        break
                path_gpt.append(each)
            else:
                good_format = False
                break
        else:
            good_format = False
            break
    return good_format, path_gpt


def verify_stepnav_simple(anno2code, g, each_json_path):
    print("verifying ", each_json_path)
    with open(each_json_path, "r") as f:
        gpt_results = json.load(f)

    src_anno = gpt_results["src_node"]
    action_requested = extract_actions(gpt_results["question"])
    path_gpt = []

    # check if each entry of path_gpt is in the correct format
    good_format, path_gpt = check_format(gpt_results)
    msg = "bad format" if not good_format else ""

    if not good_format:
        verify_result = False
        return verify_result, {
            "verify_result": verify_result,
            "src_anno": src_anno,
            "action_requested": action_requested,
            "dst_gpt": None,
            "dst_requested": None,
            "dist_shortest": len(action_requested),
            "verify_msg": msg,
        }

    dst_gpt = anno_to_code(path_gpt[-1]["node"], anno2code)
    dst_requested, msg = walk_path_to_dst(g, src_anno, action_requested, anno2code)

    # check if the dst node is correct
    if (
        dst_requested is None
        or dst_gpt is None
        or dst_gpt.lower() != dst_requested.lower()
    ):
        print("wrong dst node", dst_gpt, dst_requested)
        verify_result = False
    else:
        print("correct")
        verify_result = True
    return verify_result, {
        "verify_result": verify_result,
        "src_anno": src_anno,
        "action_requested": action_requested,
        "dst_gpt": dst_gpt,
        "dst_requested": dst_requested,
        "dist_shortest": len(action_requested),
        "verify_msg": msg,
    }


def verify_stepnav(anno2code, g, each_json_path):
    print("verifying ", each_json_path)
    with open(each_json_path, "r") as f:
        gpt_results = json.load(f)

    src_anno = gpt_results["src_node"]
    action_requested = extract_actions(gpt_results["question"])
    path_gpt = []

    # check if each entry of path_gpt is in the correct format
    good_format, path_gpt = check_format(gpt_results)
    msg = "bad format" if not good_format else ""

    # check if each action in path_gpt matches the action requested
    if good_format:
        # check if length of path_gpt is the same as length of action_requested
        if len(path_gpt) != len(action_requested):
            print("wrong length", len(path_gpt), len(action_requested))
            msg = "wrong length: generated != requested"
            good_format = False
        else:
            for i, each in enumerate(path_gpt):
                if each["action"] != action_requested[i]:
                    print("wrong action", each["action"], action_requested[i])
                    msg = "wrong action: generated != requested"
                    good_format = False
                    break

    verify_result = False
    if good_format:
        stop_node_code, stop_step, path_labeled, msg = walk_and_label_path(
            g, src_anno, path_gpt, anno2code
        )
        if msg == "all good":
            print("correct")
            verify_result = True
            # FIXME: need to check if path is as required
        print()

        verify_pack = {
            "verify_result": verify_result,
            "src_anno": src_anno,
            "action_requested": action_requested,
            "stop_step": stop_step,
            "stop_node_code": stop_node_code,
            "verify_msg": msg,
            "path_checked": path_labeled,
        }
    else:
        verify_pack = {
            "verify_result": verify_result,
            "src_anno": src_anno,
            "action_requested": action_requested,
            "stop_step": -3,  # -3 means bad format, -2 means empty path, -1 means bad src node, 0 means bad 1st prev_node.
            "stop_node_code": None,
            "verify_msg": msg,
            "path_checked": gpt_results["path"],
        }
    return verify_result, verify_pack


def extract_actions(string):
    start_index = string.find("['")
    end_index = string.find("']")
    actions_string = string[start_index + 2 : end_index]
    actions = actions_string.split("', '")
    return actions


def plot_length_dist(each_version, length_count, plot_dir):
    plt.figure(figsize=(20, 12))
    plt.bar(length_count.keys(), length_count.values(), width=0.7)
    plt.xticks(
        np.arange(min(length_count.keys()), max(length_count.keys()) + 1, 1.0),
        rotation=15,
    )
    plt.xlabel("length of path")
    plt.ylabel("count")
    plt.title(f"length distribution of {each_version}")
    plt.savefig(os.path.join(plot_dir, each_version, "length_distribution.png"))
    plt.clf()


def plot_error_type_dist(
    each_version, error_type_step_count, error_type_step_count_mean, plot_dir
):
    plt.figure(figsize=(20, 12))
    for each_error_type in error_type_step_count:
        plt.bar(each_error_type, error_type_step_count_mean[each_error_type], width=0.7)
    plt.legend(error_type_step_count.keys(), loc="upper left")
    # plt.xticks(rotation=15, ha='right') with full ticks step 1
    plt.xticks(rotation=15, ha="right")
    plt.xlabel("error type")
    plt.ylabel("mean of stop step")
    plt.title(f"error type distribution of {each_version}")
    plt.savefig(os.path.join(plot_dir, each_version, "error_type_distribution.png"))
    plt.clf()


def plot_error_type_dist_count(each_version, error_type_step_count, plot_dir):
    plt.figure(figsize=(20, 12))
    for each_error_type in error_type_step_count:
        plt.bar(each_error_type, len(error_type_step_count[each_error_type]), width=0.7)
    plt.legend(error_type_step_count.keys(), loc="upper left")
    plt.xticks(rotation=15, ha="right")
    plt.xlabel("error type")
    plt.ylabel("count")
    plt.title(f"error type distribution of {each_version}")
    plt.savefig(
        os.path.join(plot_dir, each_version, "error_type_distribution_count.png")
    )
    plt.clf()


def plot_stop_step_dists(each_version, error_type_step_count, plot_dir):
    plt.figure(figsize=(20, 12))
    for each_error_type in error_type_step_count:
        if len(error_type_step_count[each_error_type]) == 0:
            continue
            # plt.hist(error_type_step_count[each_error_type]) same bin size but smaller in visual
        plt.hist(
            error_type_step_count[each_error_type],
            bins=range(
                min(error_type_step_count[each_error_type]),
                max(error_type_step_count[each_error_type]) + 1,
                1,
            ),
        )
        plt.xticks(rotation=15)
        plt.xlabel("stop step")
        plt.ylabel("count")
        plt.title(f"stop step distribution of {each_error_type}")
        # camel case of each_error_type
        each_error_type_camel = (
            each_error_type.title().replace(" ", "").replace(":", "")
        )
        plt.savefig(
            os.path.join(
                plot_dir,
                each_version,
                f"stop_step_distribution_{each_error_type_camel}.png",
            )
        )
        plt.clf()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--maps_dir", "-m", type=str, default="./data/maps", help="path to maps folder"
    )
    parser.add_argument("--game", "-g", type=str, required=True, help="game name")
    parser.add_argument(
        "--gpt_result_dir",
        "-r",
        type=str,
        required=True,
        help="path to gpt result files",
    )
    parser.add_argument(
        "--output_dir", "-odir", type=str, required=True, help="path to output file"
    )
    # toggle to use simple function, "--simple" or "-s"
    parser.add_argument(
        "--simple",
        "-s",
        action="store_true",
        help="use simple function to check path",
    )
    args = parser.parse_args()
    return args


def recompute_for_uuid(verify_json):
    """
    there might be multiple runs of the same test
    but we only want to count the best of each test
    identify the best of each test by uuid
    """
    with open(verify_json, "r") as f:
        verify_dupli = json.load(f)
    gpt_prompt_versions = list(verify_dupli.keys())
    # "pathgen-gpt-3.5-turbo/": {
    #     "correct_num": 51,
    #     "total_num": 220,
    #     "accuracy": 0.2318181818181818,
    #     "collection": {
    # run check on each version individually, go over collection of each version

    # compute best on micro uuid
    for each_version in gpt_prompt_versions:
        current_collection = verify_dupli[each_version]["collection"]
        (
            micro_uuid_best,
            macro_uuid_best,
            micro_length_acc,
            macro_length_acc,
        ) = counting_on_level(current_collection)

        # update collection with best of each uuid and recalculate accuracy

        # recalculate micro metrics
        verify_dupli = verify_amend_acc(
            verify_dupli,
            each_version,
            current_collection,
            micro_uuid_best,
            level="micro",
        )

        # recalculate macro metrics
        verify_dupli = verify_amend_acc(
            verify_dupli,
            each_version,
            current_collection,
            macro_uuid_best,
            level="macro",
        )

        # plot acc vs length
        plot_acc_vs_dist(verify_json, each_version, micro_length_acc, macro_length_acc)

    # dump back to verify_json
    with open(verify_json, "w") as f:
        json.dump(verify_dupli, f, indent=4)


def counting_on_level(current_collection):
    macro_uuid_best, macro_length_acc = __count_helper(
        current_collection, level="macro"
    )
    micro_uuid_best, micro_length_acc = __count_helper(
        current_collection, level="micro"
    )

    return micro_uuid_best, macro_uuid_best, micro_length_acc, macro_length_acc


def __count_helper(current_collection, level):
    level_uuid_best = {}
    level_length_acc = {}

    for each_entry_name, each_entry in current_collection.items():
        level_uuid = each_entry[f"{level}_uuid"]
        verify_result = each_entry["verify_result"]
        dist_shortest = each_entry["dist_shortest"]

        # accumulate length and accuracy for each macro uuid
        if dist_shortest not in level_length_acc:
            level_length_acc[dist_shortest] = {
                "good": 0,
                "bad": 0,
            }
        if verify_result:
            level_length_acc[dist_shortest]["good"] += 1
        else:
            level_length_acc[dist_shortest]["bad"] += 1

        # find best of each macro uuid
        if level_uuid not in level_uuid_best:
            level_uuid_best[level_uuid] = (verify_result, each_entry_name)
        else:
            if level_uuid_best[level_uuid][0] < verify_result:
                level_uuid_best[level_uuid] = (verify_result, each_entry_name)

    return level_uuid_best, level_length_acc


def verify_amend_acc(
    verify_dupli, each_version, current_collection, level_uuid_best, level
):
    correct_num_level = 0
    verify_dupli[each_version][f"collection_{level}"] = []

    for each_uuid in level_uuid_best:
        verify_dupli[each_version][f"collection_{level}"].append(
            current_collection[level_uuid_best[each_uuid][1]]
        )
        if level_uuid_best[each_uuid][0] == 1:
            correct_num_level += 1
    verify_dupli[each_version][f"correct_num_{level}"] = correct_num_level
    verify_dupli[each_version][f"total_num_{level}"] = len(level_uuid_best)
    verify_dupli[each_version][f"accuracy_{level}"] = correct_num_level / len(
        level_uuid_best
    )
    return verify_dupli


def plot_acc_vs_dist(verify_json, each_version, micro_length_acc, macro_length_acc):
    micro_length_acc = sorted(micro_length_acc.items(), key=lambda x: x[0])
    macro_length_acc = sorted(macro_length_acc.items(), key=lambda x: x[0])
    micro_length = [each[0] for each in micro_length_acc]
    micro_acc = [
        each[1]["good"] / (each[1]["good"] + each[1]["bad"])
        for each in micro_length_acc
    ]
    macro_length = [each[0] for each in macro_length_acc]
    macro_acc = [
        each[1]["good"] / (each[1]["good"] + each[1]["bad"])
        for each in macro_length_acc
    ]
    # subplot for micro and macro
    fig, axs = plt.subplots(2, 1, figsize=(10, 10))
    axs[0].plot(micro_length, micro_acc)
    axs[0].set_xlabel("dist(src, dst))")
    axs[0].set_ylabel("accuracy")
    axs[0].set_title("accuracy vs dist(src, dst) - micro")
    axs[1].plot(macro_length, macro_acc)
    axs[1].set_xlabel("dist(src, dst)")
    axs[1].set_ylabel("accuracy")
    axs[1].set_title("accuracy vs dist(src, dst) - macro")
    # get verify_dir from verify_json
    verify_dir = os.path.dirname(verify_json)
    plt.savefig(
        os.path.join(verify_dir, f"{each_version.split('/')[0]}_acc_vs_length.png")
    )
    plt.close()


def random_guess_rate(all2all, code2anno):
    """
    for stepnav, random guess correctness rate is 1/num_locations
    for pathgen, random guess correctness rate is (1/{num_actions + stop})^avg_path_len
    """
    total_steps = 0
    total_entries = float(len(all2all))
    for each in all2all:
        total_steps += int(each["step_count"])
    avg_entries = total_steps / total_entries

    total_locs = len(code2anno.keys())

    stepnav_random_guess_rate = 1.0 / total_locs
    pathgen_random_guess_rate = math.pow(1.0 / (total_locs + 1), avg_entries)
    return stepnav_random_guess_rate, pathgen_random_guess_rate


if __name__ == "__main__":
    # argparse to readin game folder
    args = parse_args()

    # test existence of game folder
    tgt_path = os.path.join(args.maps_dir, args.game)
    if not os.path.exists(tgt_path):
        print("path does not exist")
        exit(1)

    # test existence of gpt result folder
    if not os.path.exists(args.gpt_result_dir):
        print("path does not exist")
        exit(1)

    # test existence of output folder
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    all2all_json = os.path.join(tgt_path, f"{args.game}.all2all.json")
    with open(all2all_json, "r") as f:
        all2all = json.load(f)

    anno2code_json = os.path.join(tgt_path, f"{args.game}.anno2code.json")
    code2anno_json = os.path.join(tgt_path, f"{args.game}.code2anno.json")
    with open(anno2code_json, "r") as f:
        anno2code = json.load(f)
        # anno2code = {k.lower(): v for k, v in anno2code.items()}
    with open(code2anno_json, "r") as f:
        code2anno = json.load(f)
        # code2anno = {k.lower(): v for k, v in code2anno.items()}

    map_file = os.path.join(tgt_path, f"{args.game}.map.human")
    map_file_reversed = os.path.join(tgt_path, f"{args.game}.map.reversed")
    g = build_graph_from_file_with_reverse(map_file, map_file_reversed, verbose=False)
    print(g.nodes)

    print("\n\n\n\n\n")

    verify_collections = {}
    gpt_result_dir = args.gpt_result_dir
    gpt_prompt_version = [
        "pathgen-gpt-3.5-turbo/",
        "pathgen-gpt-4/",
        "stepnav-gpt-3.5-turbo/",
        "stepnav-gpt-4/",
    ]
    random_guess_rate_stepnav, random_guess_rate_pathgen = random_guess_rate(
        all2all, code2anno
    )

    for each_version in gpt_prompt_version:
        current_path = f"{gpt_result_dir}/{each_version}"
        # get a list of all files in the directory using glob
        gpt_result_jsons = glob.glob(os.path.join(current_path, "*.json"))

        correct = 0
        total = 0
        current_collection = {}
        for each_json in gpt_result_jsons:
            micro_uuid = compute_json_uuid(each_json, level="micro")
            macro_uuid = compute_json_uuid(each_json, level="macro")
            if "pathgen" in each_version:
                if args.simple:
                    verify_result, verify_pack = verify_pathgen_simple(
                        g, anno2code, each_json
                    )
                else:
                    verify_result, verify_pack = verify_pathgen(g, anno2code, each_json)
            elif "stepnav" in each_version:
                if args.simple:
                    verify_result, verify_pack = verify_stepnav_simple(
                        anno2code, g, each_json
                    )
                else:
                    verify_result, verify_pack = verify_stepnav(anno2code, g, each_json)

            if verify_result:
                correct += 1
            total += 1
            verify_pack["micro_uuid"] = micro_uuid
            verify_pack["macro_uuid"] = macro_uuid
            current_collection[each_json] = verify_pack

        random_guess = (
            random_guess_rate_pathgen
            if "pathgen" in each_version
            else random_guess_rate_stepnav
        )
        verify_collections[each_version] = {
            "correct_num": correct,
            "total_num": total,
            "accuracy": correct / total,
            "collection": current_collection,
            "random_guess_rate": random_guess,
        }

    if args.simple:
        json_output = os.path.join(
            args.output_dir, args.game, "verify_results_simple.json"
        )
    else:
        json_output = os.path.join(args.output_dir, args.game, "verify_results.json")
    with open(json_output, "w") as f:
        json.dump(verify_collections, f, indent=4)
    recompute_for_uuid(json_output)

    if not args.simple:
        # compute stats from verify_collections
        for each_version in gpt_prompt_version:
            # for each type of error in PathCheck, count its appearance in the collection
            # error_count is of the same keys as the PathCheck
            error_type_step_count = {v: [] for v in PathCheck.values()}
            error_type_step_count_mean = {}
            length_count = {}

            for each_pack in verify_collections[each_version]["collection"].values():
                verify_result = each_pack["verify_result"]
                stop_step = each_pack["stop_step"]
                verify_msg = each_pack["verify_msg"]
                path_checked = each_pack["path_checked"]

                # get length of path_checked
                if len(path_checked) not in length_count:
                    length_count[len(path_checked)] = 1
                else:
                    length_count[len(path_checked)] += 1

                # get error count
                if verify_msg not in error_type_step_count:
                    error_type_step_count[verify_msg] = [int(stop_step)]
                else:
                    error_type_step_count[verify_msg].append(int(stop_step))

                # locate error path by finding the last entry of path with "msg"
                if stop_step >= 0 and verify_msg == PathCheck[6]:
                    wrong_step = path_checked[stop_step]
                    wrong_src_anno = wrong_step["prev_node"]
                    wrong_dst_anno = wrong_step["node"]
                    wrong_src_code = anno_to_code(wrong_src_anno, anno2code)
                    wrong_dst_code = anno_to_code(wrong_dst_anno, anno2code)
                    wrong_action = wrong_step["action"]
                    # check if g.forward has (wrong_src_code, wrong_dst_code)
                    if g.forward.has_edge(wrong_src_code, wrong_dst_code):
                        error_type_step_count[PathCheck[7]].append(int(stop_step))
                    else:
                        error_type_step_count[PathCheck[8]].append(int(stop_step))

            # # drop GOOD: *
            # error_type_step_count.pop(PathCheck[7], None)
            # error_type_step_count.pop(PathCheck[8], None)

            # compute mean of each error type
            for each_error_type, stop_step_list in error_type_step_count.items():
                error_type_step_count_mean[each_error_type] = np.mean(stop_step_list)

            print("length_count", length_count)
            print("error_type_step_count", error_type_step_count)
            print()

            plot_dir = os.path.join(args.output_dir, args.game, "eval_plots")
            # make dir for each version
            if not os.path.exists(os.path.join(plot_dir, f"{each_version}")):
                os.makedirs(os.path.join(plot_dir, f"{each_version}"))

            # matplotlib plot histogram of length_count, bar label pointing at the center of each bar
            plot_length_dist(each_version, length_count, plot_dir)

            # matplotlib plot means of error_type_step_count, no bar label, use legend instead, with digits on top of each bar
            plot_error_type_dist(
                each_version,
                error_type_step_count,
                error_type_step_count_mean,
                plot_dir,
            )

            # matplotlib plot histogram of error_type_step_count
            plot_error_type_dist_count(each_version, error_type_step_count, plot_dir)

            # matplotlib plot distribution of stop_step for each error type
            plot_stop_step_dists(each_version, error_type_step_count, plot_dir)