import argparse
import json
import math
import os
import sys
import uuid

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from gen_paths.digraph import anno_to_code
from gen_paths.utils import compute_hash


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
    parser.add_argument(
        "--cutoff_json", "-c", type=str, required=True, help="path to cutoff json file"
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
        str_pack = f"{src_node}_{dst_node}_{task}_{path_gt}"
    elif level == "macro":
        str_pack = f"{src_node}_{dst_node}_{task}"
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


def check_format(gpt_results, dst_only=False):
    # replace all "location_before" and "location_after" with "prev_node" and "node"
    replace_key(gpt_results, "location_before", "prev_node")
    replace_key(gpt_results, "location_after", "node")

    good_format = True
    path_gpt = []
    if "path" not in gpt_results:
        good_format = False
        return good_format, path_gpt

    if dst_only:
        if len(gpt_results["path"]) == 0:
            good_format = True
            return good_format, path_gpt
        last_element = gpt_results["path"][-1]
        # print(f"last element is {last_element}")
        if isinstance(last_element, dict):
            # print("last element is a dict")
            if ("prev_node" in last_element and "node" in last_element) or (
                "location_before" in last_element and "location_after" in last_element
            ):
                # print("last element has the correct keys")
                path_gpt.append(last_element)
            else:
                good_format = False
            return good_format, path_gpt
        else:
            return False, path_gpt

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
    level_length_acc = {}

    for each_entry in current_collection:
        # level_uuid = each_entry[f"{level}_uuid"]
        verify_result = each_entry["verify_result"]
        dist_shortest = each_entry[field]
        # when connectivity is False, the dist_shortest is None!
        if dist_shortest is None:
            continue

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
    verify_dupli[each_version][f"accuracy_{level}"] = (
        correct_num_level / len(level_uuid_best) if len(level_uuid_best) != 0 else 0
    )
    return verify_dupli


def skip_due_to_cutoff(
    task, each_json, global_cutoff_step, anno2code, all_pairs=None, all2all=None
):
    # all_pairs must be provided when task == "desti"
    # all2all must be provided when task == "route"
    assert task in ["desti", "route"], "task must be either desti or route"
    if task == "desti":
        assert all_pairs is not None, "all_pairs must be provided"
    elif task == "route":
        assert all2all is not None, "all2all must be provided"

    # load the json file
    with open(each_json, "r") as f:
        gpt_result = json.load(f)
    min_cutoff_required = None

    if task == "desti":
        dst_anno = gpt_result["dst_node"]
        dst_code = anno_to_code(dst_anno, anno2code)
        src_anno = gpt_result["src_node"]
        src_code = anno_to_code(src_anno, anno2code)
        # find matching entry in all_pairs with src_code and dst_code
        matching_entry = None
        for each_entry in all_pairs:
            if (
                each_entry["src_node"] == src_code
                and each_entry["dst_node"] == dst_code
            ):
                matching_entry = each_entry
                break
        assert matching_entry is not None, "matching entry not found"
        min_cutoff_required = min(matching_entry["path_min_cutoffs"])
        # print(f"min_cutoff_required: [{min_cutoff_required}]")

    elif task == "route":
        dst_anno = gpt_result["dst_node"]
        dst_code = anno_to_code(dst_anno, anno2code)
        src_anno = gpt_result["src_node"]
        src_code = anno_to_code(src_anno, anno2code)
        # find matching entry in all_pairs with src_code and dst_code
        matching_entry = []
        for each_entry in all2all:
            if (
                each_entry["src_node"] == src_code
                and each_entry["dst_node"] == dst_code
            ):
                matching_entry.append(each_entry)
        if len(matching_entry) == 0:
            print(
                f"matched path not found for given gpt result: [{each_json}], LIKELY IT'S A NON_CONNECTED PAIR [{src_code}] -> [{dst_code}]"
            )
            return False

        # compare the cutoff step
        matched_cutoffs = [each["path_min_cutoff"] for each in matching_entry]
        assert len(matched_cutoffs) > 0, f"[{each_json}]: matched_cutoffs is empty"
        min_cutoff_required = min(matched_cutoffs)

    assert min_cutoff_required is not None, "min_cutoff_required is None"

    if min_cutoff_required > global_cutoff_step:
        print(f"min_cutoff_required: [{min_cutoff_required}]")
        print(f"global_cutoff_step: [{global_cutoff_step}]")
        print(f"skipping: [{each_json}]")
        return True
    return False


def replace_key(json_obj, old_key, new_key):
    if isinstance(json_obj, dict):
        for key in list(json_obj.keys()):
            if key == old_key:
                json_obj[new_key] = json_obj.pop(key)
            else:
                replace_key(json_obj[key], old_key, new_key)
    elif isinstance(json_obj, list):
        for item in json_obj:
            replace_key(item, old_key, new_key)
