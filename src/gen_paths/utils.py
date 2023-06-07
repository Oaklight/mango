# color print without extra library, in green
import argparse
import hashlib
import json


def print_green(text, inline=False):
    if not inline:
        print("\033[92m {}\033[00m".format(text))
    else:
        print("\033[92m {}\033[00m".format(text), end="")


# , red, bold black
def print_red(text, inline=False):
    if not inline:
        print("\033[91m {}\033[00m".format(text))
    else:
        print("\033[91m {}\033[00m".format(text), end="")


# , bold black
def print_black(text, inline=False):
    if not inline:
        print("\033[1m {}\033[00m".format(text))
    else:
        print("\033[1m {}\033[00m".format(text), end="")


# general color print, receive txt and color
def print_color(text, color, inline=False):
    if color == "green" or color == "g":
        print_green(text, inline)
    elif color == "red" or color == "r":
        print_red(text, inline)
    elif color == "black" or color == "b":
        print_black(text, inline)
    else:
        print(text, end="" if inline else "\n")


# general input with color, receive txt and color
def input_color(text, color, inline=False):
    if color == "green" or color == "g":
        print_green(text, inline)
    elif color == "red" or color == "r":
        print_red(text, inline)
    elif color == "black" or color == "b":
        print_black(text, inline)
    else:
        print(text, end="" if inline else "\n")
    return input()


# a markdown line is either H1, H2, plain text, or empty.
# return type and content.
# There is no other type of line in the markdown file
# raise error if line is not one of the four types
def parse_line(line: str) -> tuple[str, str]:
    str_type = None
    content = None
    line = line.strip()
    if line == "":
        str_type = "empty"
        content = ""
    elif line.startswith("# "):
        str_type = "H1"
        content = line[2:]
    elif line.startswith("## "):
        str_type = "H2"
        content = line[3:]
    else:
        str_type = "plain"
        content = line

    return str_type, content.strip().lower()


def extract_direction_text(line: str) -> tuple[str, str]:
    action, to_where = [each.strip().lower() for each in line.split("-->")]
    return action, to_where


def extract_item_text(line: str) -> tuple[str, str, str]:
    name = line.split("(")[0].strip()
    description = line.split("(")[1].split(")")[0].strip()
    actions = line.split("[")[1].split("]")[0].strip()
    return name, description, actions


def get_args_all2all():
    parser = argparse.ArgumentParser()
    parser.add_argument("--map", "-m", type=str, required=True)

    # mutually exclusive group for actions and reverse_map
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--actions", "-a", type=str)
    group.add_argument("--reverse_map", "-r", type=str)

    parser.add_argument("--output_dir", "-odir", type=str)
    parser.add_argument("--node_step_map", "-nsm", type=str)
    args = parser.parse_args()

    # output_dir is default to be the same as map file
    if args.output_dir is None:
        args.output_dir = "/".join(args.map.split("/")[:-1]) + "/"
    if args.output_dir[-1] != "/":
        args.output_dir += "/"

    # output_path is default to be the same as map file, with .all2all.json
    args.output_path = (
        args.output_dir + args.map.split("/")[-1].split(".")[0] + ".all2all.json"
    )

    print_args(args)
    return args


def print_args(args):
    # for each of args' attributes, print it out. Using vars(args) returns a dict
    for k, v in vars(args).items():
        print_color(f"\t{k}: ", "b", inline=True)
        print(v)


def confirm_continue():
    confirm = input_color("Continue? (y/n) ", "b", inline=True)
    if confirm == "y":
        pass
    else:
        print_color("Aborted!", "b")
        exit(1)


def compute_hash(json_obj, mode, del_diff_shortest=False):
    accept_modes = ["all2all", "all_pairs", "path_details", "anno2code", "code2anno"]
    assert mode in accept_modes, f"mode must be one of {accept_modes}"

    # make deep copy of json_obj
    # json_obj_copy = json_obj.copy() AttributeError: 'str' object has no attribute 'copy'
    json_obj_copy = json.loads(json.dumps(json_obj))
    delete_keys_all2all = [
        "seen",
        "seen_in_forward",
        "step_min_cutoff",
        "path_min_cutoff",
        "all_steps_seen_in_forward",
        # "diff_shortest",
    ]
    delete_keys_allpairs = [
        "num_paths",
        "path_min_cutoffs",
    ]  # "diff_shortest"
    if del_diff_shortest == True:
        delete_keys_all2all.append("diff_shortest")
        delete_keys_allpairs.append("diff_shortest")

    # for key in delete_keys:
    #     if key in json_obj_copy:
    #         del json_obj_copy[key]
    if mode == "all2all":
        path_details = json_obj_copy["path_details"]
        for i, entry in enumerate(path_details):
            for key in delete_keys_all2all:
                if key in entry:
                    del entry[key]
            path_details[i] = entry
        json_obj_copy["path_details"] = path_details
        for key in delete_keys_all2all:
            if key in json_obj_copy:
                del json_obj_copy[key]
    elif mode == "all_pairs":
        for key in delete_keys_allpairs:
            if key in json_obj_copy:
                del json_obj_copy[key]
    elif mode == "path_details":
        for i, entry in enumerate(json_obj_copy):
            for key in delete_keys_all2all:
                if key in entry:
                    del entry[key]
            json_obj_copy[i] = entry
    else:
        # print(f"skip {mode}")
        pass

    json_str = json.dumps(json_obj_copy, sort_keys=True)
    # json_str = json_str.replace('"seen": true,', "")
    hash_object = hashlib.md5(json_str.encode())
    return hash_object.hexdigest()


def compare_path_details(path1, path2):
    # path1 is newer version, path2 is older version
    assert len(path1) == len(path2), f"len(path1)={len(path1)}, len(path2)={len(path2)}"

    for i in range(len(path1)):
        prev_node_1 = path1[i]["prev_node"]
        prev_node_2 = path2[i]["prev_node"]
        node_1 = path1[i]["node"]
        node_2 = path2[i]["node"]
        action_1 = path1[i]["action"]
        action_2 = path2[i]["action"]
        seen_1 = (
            path1[i]["seen_in_forward"]
            if "seen_in_forward" in path1[i]
            else path1[i]["seen"]
        )
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
