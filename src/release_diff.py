import csv
import glob
import json
import os
import sys

current = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current)

from gen_paths.utils import compute_hash
from matplotlib import pyplot as plt


def find_difference(json1, json2, mode="all2all"):
    # json2 is newer one. I want to know which of json2 is different from json1, or not in json1
    with open(json1) as file1, open(json2) as file2:
        data1 = json.load(file1)
        data2 = json.load(file2)

    dict1 = {compute_hash(obj, mode): obj for obj in data1}
    dict2 = {compute_hash(obj, mode): obj for obj in data2}

    # same keys
    same_keys = set(dict1.keys()).intersection(set(dict2.keys()))
    # residual keys from dict2
    new_keys = set(dict2.keys()) - same_keys
    # different keys
    drop_keys = set(dict1.keys()) - same_keys

    new_objects = [dict2[key] for key in new_keys]
    drop_objects = [dict1[key] for key in drop_keys]
    same_objects = [dict1[key] for key in same_keys]

    return new_objects, drop_objects, same_objects


# now check difference of *.code2anno.json in each folder from intersect_data_path
def check_dump_diff(
    find_difference, latest_data_path, old_data_path, diff_data_path, each, tgt_file
):
    old_file_path = f"{old_data_path[each]}/{each}.{tgt_file}.json"
    new_file_path = f"{latest_data_path[each]}/{each}.{tgt_file}.json"

    # find_difference
    new_objects, drop_objects, same_objects = find_difference(
        old_file_path, new_file_path, mode=tgt_file
    )

    print(f"Found {len(new_objects)} new objects, {len(drop_objects)} dropped objects.")
    print()

    if len(new_objects) != 0 or len(drop_objects) != 0:
        # test or create folder
        each_diff_path = f"{diff_data_path}/{each}"
        if not os.path.exists(each_diff_path):
            os.makedirs(each_diff_path)

    if len(new_objects) != 0:
        additional_file_path = f"{each_diff_path}/{each}.{tgt_file}.new.json"
        if tgt_file != "all_pairs":
            new_objects = sorted(
                new_objects,
                key=lambda x: (
                    x["src_node"],
                    x["dst_node"],
                    x["diff_shortest"],
                    x["step_count"],
                    x["path_details"][0]["prev_node"],
                    x["path_details"][0]["node"],
                    x["path_details"][0]["action"],
                ),
            )
        else:
            new_objects = sorted(
                new_objects,
                key=lambda x: (
                    x["src_node"],
                    x["dst_node"],
                    x["num_paths"],
                ),
            )
        # dump new object to additional_file_path
        with open(additional_file_path, "w") as f:
            json.dump(new_objects, f, indent=4)

    if len(drop_objects) != 0:
        dropped_file_path = f"{each_diff_path}/{each}.{tgt_file}.drop.json"
        if tgt_file != "all_pairs":
            drop_objects = sorted(
                drop_objects,
                key=lambda x: (
                    x["src_node"],
                    x["dst_node"],
                    x["diff_shortest"],
                    x["step_count"],
                    x["path_details"][0]["prev_node"],
                    x["path_details"][0]["node"],
                    x["path_details"][0]["action"],
                ),
            )
        else:
            drop_objects = sorted(
                drop_objects,
                key=lambda x: (
                    x["src_node"],
                    x["dst_node"],
                    x["num_paths"],
                ),
            )
        # dump dropped object to dropped_file_path
        with open(dropped_file_path, "w") as f:
            json.dump(drop_objects, f, indent=4)

    diff_shortest_dict_add = {}
    step_count_dict_add = {}
    diff_shortest_dict_drop = {}
    step_count_dict_drop = {}
    all_pairs_old = {}

    if tgt_file == "all2all":
        # plot distribution histogram of diff_shortest and step_count
        for each in new_objects:
            diff_shortest_dict_add[each["diff_shortest"]] = (
                diff_shortest_dict_add.get(each["diff_shortest"], 0) + 1
            )
            step_count_dict_add[each["step_count"]] = (
                step_count_dict_add.get(each["step_count"], 0) + 1
            )

        for each in drop_objects:
            diff_shortest_dict_drop[each["diff_shortest"]] = (
                diff_shortest_dict_drop.get(each["diff_shortest"], 0) + 1
            )
            step_count_dict_drop[each["step_count"]] = (
                step_count_dict_drop.get(each["step_count"], 0) + 1
            )
            pair_name = f"{each['src_node']} -> {each['dst_node']}"
            if pair_name not in all_pairs_old:
                all_pairs_old[pair_name] = {
                    "src_node": each["src_node"],
                    "dst_node": each["dst_node"],
                    "num_paths": 0,
                }
            all_pairs_old[pair_name]["num_paths"] += 1

        for each in same_objects:
            pair_name = f"{each['src_node']} -> {each['dst_node']}"
            if pair_name not in all_pairs_old:
                all_pairs_old[pair_name] = {
                    "src_node": each["src_node"],
                    "dst_node": each["dst_node"],
                    "num_paths": 0,
                }
            all_pairs_old[pair_name]["num_paths"] += 1

    return (
        len(new_objects),
        len(drop_objects),
        len(same_objects),
        (diff_shortest_dict_add, step_count_dict_add),
        (diff_shortest_dict_drop, step_count_dict_drop),
        list(all_pairs_old.values()),
    )


if __name__ == "__main__":
    latest_data_path = "./data/maps-release"

    old_data_path = ["../gpt-games/maps_batch_1", "../gpt-games/maps_batch_2"]
    diff_data_path = "./data/maps-diff-fjd"

    # old_data_path = "./data/maps-release-copy"
    # diff_data_path = "./data/maps-diff-copy"

    # test path existence or create
    if not os.path.exists(diff_data_path):
        os.makedirs(diff_data_path)

    # glob to get all folder names in all elements from old_data_path, and only the last layer folder name then flatten the list
    old_data_path = [glob.glob(f"{each}/*") for each in old_data_path]
    old_data_path = [item for sublist in old_data_path for item in sublist]

    # old_data_path = glob.glob(f"{old_data_path}/*")

    # get the last layer folder name, use it as key, and path as value
    old_data_path = {each.split("/")[-1]: each for each in old_data_path}
    # print(old_data_path)

    # get all folder name in latest_data_path
    latest_data_path = glob.glob(f"{latest_data_path}/*")
    # get the last layer folder name, use it as key, and path as value
    latest_data_path = {each.split("/")[-1]: each for each in latest_data_path}
    # print(latest_data_path)

    # check their intersections
    intersect_data_path = set(old_data_path.keys()).intersection(
        set(latest_data_path.keys())
    )
    print("intersect_data_path: ", intersect_data_path)

    # check difference of each folder
    anno2code_drop, anno2code_add = 0, 0
    code2anno_drop, code2anno_add = 0, 0
    all2all_drop, all2all_add = 0, 0
    allpairs_drop, allpairs_add = 0, 0
    diff_num_dict = {}

    for each in intersect_data_path:
        print(f"Checking {each}...")

        tgt_file = "anno2code"
        anno2code_add, anno2code_drop, anno2code_same, _, _, _ = check_dump_diff(
            find_difference,
            latest_data_path,
            old_data_path,
            diff_data_path,
            each,
            tgt_file,
        )

        tgt_file = "code2anno"
        code2anno_add, code2anno_drop, code2anno_same, _, _, _ = check_dump_diff(
            find_difference,
            latest_data_path,
            old_data_path,
            diff_data_path,
            each,
            tgt_file,
        )

        tgt_file = "all2all"
        (
            all2all_add,
            all2all_drop,
            all2all_same,
            all2all_add_stats,
            all2all_drop_stats,
            all_pairs_old,
        ) = check_dump_diff(
            find_difference,
            latest_data_path,
            old_data_path,
            diff_data_path,
            each,
            tgt_file,
        )

        # dump all_pair_old, sort first
        all_pairs_old = sorted(
            all_pairs_old,
            key=lambda x: (x["src_node"], x["dst_node"], x["num_paths"]),
        )
        with open(
            f"{old_data_path[each]}/{each}.all_pairs.json", "w", encoding="utf-8"
        ) as f:
            json.dump(all_pairs_old, f, indent=4)

        tgt_file = "all_pairs"
        allpairs_add, allpairs_drop, allpairs_same, _, _, _ = check_dump_diff(
            find_difference,
            latest_data_path,
            old_data_path,
            diff_data_path,
            each,
            tgt_file,
        )

        # add to dict if there is any difference
        if (
            anno2code_drop != 0
            or anno2code_add != 0
            or code2anno_drop != 0
            or code2anno_add != 0
            or all2all_drop != 0
            or all2all_add != 0
            or allpairs_drop != 0
            or allpairs_add != 0
        ):
            diff_num_dict[each] = {
                "anno2code_drop": anno2code_drop,
                "anno2code_add": anno2code_add,
                "anno2code_same": anno2code_same,
                "code2anno_drop": code2anno_drop,
                "code2anno_add": code2anno_add,
                "code2anno_same": code2anno_same,
                "all2all_drop": all2all_drop,
                "all2all_add": all2all_add,
                "all2all_same": all2all_same,
                "all2all_rate": (all2all_add + all2all_same)
                / float(all2all_same + all2all_drop),
                "allpairs_drop": allpairs_drop,
                "allpairs_add": allpairs_add,
                "allpairs_same": allpairs_same,
                "allpairs_rate": (allpairs_add + allpairs_same)
                / float(allpairs_same + allpairs_drop),
            }

            diff_shortest_dict_add, step_count_dict_add = all2all_add_stats
            diff_shortest_dict_drop, step_count_dict_drop = all2all_drop_stats

            # plot distribution histogram of diff_shortest
            plt.figure(figsize=(20, 10))
            plt.subplot(1, 2, 1)
            plt.bar(
                diff_shortest_dict_add.keys(),
                diff_shortest_dict_add.values(),
                color="g",
                width=0.5,
            )
            # fix x range
            plt.xlim(0, 30)
            plt.title(f"diff_shortest distribution of all2all added")
            plt.xlabel("diff_shortest")
            plt.ylabel("count")
            plt.subplot(1, 2, 2)
            plt.bar(
                step_count_dict_add.keys(),
                step_count_dict_add.values(),
                color="g",
                width=0.5,
            )
            plt.xlim(0, 30)
            plt.title(f"step_count distribution of all2all added")
            plt.xlabel("step_count")
            plt.ylabel("count")
            plt.savefig(f"{diff_data_path}/{each}_all2all_diff_add_stats.png")
            plt.close()

            # plot distribution histogram of step_count
            plt.figure(figsize=(20, 10))
            plt.subplot(1, 2, 1)
            plt.bar(
                diff_shortest_dict_drop.keys(),
                diff_shortest_dict_drop.values(),
                color="r",
                width=0.5,
            )
            plt.xlim(0, 30)
            plt.title(f"diff_shortest distribution of all2all dropped")
            plt.xlabel("diff_shortest")
            plt.ylabel("count")
            plt.subplot(1, 2, 2)
            plt.bar(
                step_count_dict_drop.keys(),
                step_count_dict_drop.values(),
                color="r",
                width=0.5,
            )
            plt.xlim(0, 30)
            plt.title(f"step_count distribution of all2all dropped")
            plt.xlabel("step_count")
            plt.ylabel("count")
            plt.savefig(f"{diff_data_path}/{each}_all2all_diff_drop_stats.png")
            plt.close()

    # drop a csv file to record the numbers
    # sort the dict by key
    diff_num_dict = dict(sorted(diff_num_dict.items()))

    with open(f"{diff_data_path}/diff_numbers.csv", "w") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "folder_name",
                "anno2code_drop",
                "anno2code_add",
                "anno2code_same",
                "code2anno_drop",
                "code2anno_add",
                "code2anno_same",
                "all2all_drop",
                "all2all_add",
                "all2all_same",
                "all2all_total_change_rate",
                "allpair_drop",
                "allpair_add",
                "allpair_same",
                "allpair_total_change_rate",
            ]
        )
        for key, val in diff_num_dict.items():
            w.writerow(
                [
                    key,
                    val["anno2code_drop"],
                    val["anno2code_add"],
                    val["anno2code_same"],
                    val["code2anno_drop"],
                    val["code2anno_add"],
                    val["code2anno_same"],
                    val["all2all_drop"],
                    val["all2all_add"],
                    val["all2all_same"],
                    val["all2all_rate"],
                    val["allpairs_drop"],
                    val["allpairs_add"],
                    val["allpairs_same"],
                    val["allpairs_rate"],
                ]
            )
