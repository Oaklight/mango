import argparse
import json
import math
import os
import sys
import uuid

from matplotlib import pyplot as plt


current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)


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
    # toggle to use verbose --verbose or -v
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="print verbose information"
    )
    args = parser.parse_args()
    args.output_dir = os.path.join(args.output_dir, args.game)

    # test existence of game folder
    args.tgt_path = os.path.join(args.maps_dir, args.game)
    if not os.path.exists(args.tgt_path):
        print("map path does not exist", args.tgt_path)
        exit(1)

    # test existence of gpt result folder
    if not os.path.exists(args.gpt_result_dir):
        print("gpt results path does not exist", args.gpt_result_dir)
        exit(1)

    # test existence of output folder
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    return args


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


def extract_actions(string):
    start_index = string.find("['")
    end_index = string.find("']")
    actions_string = string[start_index + 2 : end_index]
    actions = actions_string.split("', '")
    return actions


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

        # update collection with best of each uuid and recalculate accuracy
        macro_uuid_best = __count_helper_best(current_collection, level="macro")
        micro_uuid_best = __count_helper_best(current_collection, level="micro")

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

        macro_acc_vs_term_dist = __count_helper_trend(
            current_collection, level="macro", field="dist_shortest"
        )
        micro_acc_vs_term_dist = __count_helper_trend(
            current_collection, level="micro", field="dist_shortest"
        )
        # plot acc vs length
        plot_acc_vs_term_dist(
            verify_json, each_version, micro_acc_vs_term_dist, macro_acc_vs_term_dist
        )

        # if "route_length" is a field of first entry of collection, then plot acc vs route length
        if "route_length" in current_collection[list(current_collection.keys())[0]]:
            macro_acc_vs_route_length = __count_helper_trend(
                current_collection, level="macro", field="route_length"
            )
            micro_acc_vs_route_length = __count_helper_trend(
                current_collection, level="micro", field="route_length"
            )
            plot_acc_vs_route_length(
                verify_json, each_version, micro_acc_vs_route_length, macro_acc_vs_route_length
            )

    # dump back to verify_json
    with open(verify_json, "w") as f:
        json.dump(verify_dupli, f, indent=4)


def __count_helper_best(current_collection, level):
    level_uuid_best = {}

    for each_entry_name, each_entry in current_collection.items():
        level_uuid = each_entry[f"{level}_uuid"]
        verify_result = each_entry["verify_result"]

        # find best of each macro uuid
        if level_uuid not in level_uuid_best:
            level_uuid_best[level_uuid] = (verify_result, each_entry_name)
        else:
            if level_uuid_best[level_uuid][0] < verify_result:
                level_uuid_best[level_uuid] = (verify_result, each_entry_name)

    return level_uuid_best


def __count_helper_trend(current_collection, level, field="dist_shortest"):
    pass
    level_length_acc = {}

    for each_entry_name, each_entry in current_collection.items():
        level_uuid = each_entry[f"{level}_uuid"]
        verify_result = each_entry["verify_result"]
        dist_shortest = each_entry[field]

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

    return level_length_acc


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


def plot_acc_vs_term_dist(
    verify_json, each_version, micro_length_acc, macro_length_acc
):
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
    axs[0].set_xlabel("dist(src, dst) - micro")
    axs[0].set_ylabel("accuracy")

    axs[1].plot(macro_length, macro_acc)
    axs[1].set_xlabel("dist(src, dst) - macro")
    axs[1].set_ylabel("accuracy")

    # get verify_dir from verify_json
    verify_dir = os.path.dirname(verify_json)
    plt.savefig(
        os.path.join(verify_dir, f"{each_version.split('/')[0]}_acc_vs_term_dist.png")
    )
    plt.close()


def plot_acc_vs_route_length(
    verify_json, each_version, micro_length_acc, macro_length_acc
):
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
    axs[0].set_xlabel("route length - micro")
    axs[0].set_ylabel("accuracy")

    axs[1].plot(macro_length, macro_acc)
    axs[1].set_xlabel("route length - macro")
    axs[1].set_ylabel("accuracy")

    # get verify_dir from verify_json
    verify_dir = os.path.dirname(verify_json)
    plt.savefig(
        os.path.join(
            verify_dir, f"{each_version.split('/')[0]}_acc_vs_route_length.png"
        )
    )
    plt.close()
