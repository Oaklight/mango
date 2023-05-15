import argparse
import glob
import json
import os

from matplotlib import pyplot as plt
import numpy as np

from digraph import (
    build_graph_from_file_with_reverse,
    walk_and_label_path,
    PathCheck,
    anno_to_code,
)


# # FIXME: use name exactly as in provided files, for example use "the troll room" instead of "troll room"
# def str_txt)
#     if str_txt == "troll room":
#         return "the troll room"
#     return str_txt


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


if __name__ == "__main__":
    # argparse to readin game folder
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
    args = parser.parse_args()

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

    map_file = os.path.join(tgt_path, f"{args.game}.map.machine")
    map_file_reversed = os.path.join(tgt_path, f"{args.game}.map.machine.reversed")
    g = build_graph_from_file_with_reverse(map_file, map_file_reversed, verbose=False)

    print("\n\n\n\n\n")

    verify_collections = {}
    gpt_result_dir = args.gpt_result_dir
    gpt_prompt_version = [
        "pathgen-gpt-3.5-turbo/",
        "pathgen-gpt-4/",
        "stepnav-gpt-3.5-turbo/",
        "stepnav-gpt-4/",
    ]

    for each_version in gpt_prompt_version:
        current_path = f"{gpt_result_dir}/{each_version}"
        # get a list of all files in the directory using glob
        gpt_result_jsons = glob.glob(os.path.join(current_path, "*.json"))

        correct = 0
        total = 0
        current_collection = {}
        for each_json in gpt_result_jsons:
            if "pathgen" in each_version:
                verify_result, verify_pack = verify_pathgen(g, anno2code, each_json)
            elif "stepnav" in each_version:
                verify_result, verify_pack = verify_stepnav(anno2code, g, each_json)

            if verify_result:
                correct += 1
            total += 1
            current_collection[each_json] = verify_pack

        verify_collections[each_version] = {
            "correct_num": correct,
            "total_num": total,
            "accuracy": correct / total,
            "collection": current_collection,
        }

    with open(
        os.path.join(args.output_dir, args.game, "verify_results.json"), "w"
    ) as f:
        json.dump(verify_collections, f, indent=4)

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
            each_version, error_type_step_count, error_type_step_count_mean, plot_dir
        )

        # matplotlib plot histogram of error_type_step_count
        plot_error_type_dist_count(each_version, error_type_step_count, plot_dir)

        # matplotlib plot distribution of stop_step for each error type
        plot_stop_step_dists(each_version, error_type_step_count, plot_dir)
