import glob
import json
import os
import re

from jericho import FrotzEnv

direction_abbrv_dict = {
    "e": "east",
    "w": "west",
    "n": "north",
    "s": "south",
    "ne": "northeast",
    "nw": "northwest",
    "se": "southeast",
    "sw": "southwest",
    "u": "up",
    "d": "down",
}  # jericho.defines.ABBRV_DICT
direction_vocab_abbrv = direction_abbrv_dict.keys()
direction_vocab = direction_abbrv_dict.values()
opposite_direction_dict = {
    "east": "west",
    "west": "east",
    "north": "south",
    "south": "north",
    "northeast": "southwest",
    "southwest": "northeast",
    "northwest": "southeast",
    "southeast": "northwest",
    "up": "down",
    "down": "up",
}


def __process_again(acts):
    for i, a in enumerate(acts):
        if a.lower() == "again":
            acts[i] = acts[i - 1]
    return acts


def load_env(args):
    # search for game_name in jericho_path. The real game file should be game_name.z3 or .z5 or .z8
    # by cross checking with entries in glob
    game_file_path = None
    for game_file in glob.glob(f"{args.jericho_path}/*"):
        if args.game_name == os.path.splitext(os.path.basename(game_file))[0]:
            game_file_path = game_file
            break
    if game_file_path is None:
        print(f"Game file {args.game_name} not found in {args.jericho_path}")
        exit(-1)
    env = FrotzEnv(game_file_path)
    return env


def load_walkthrough_acts(args, env, keep_again: bool = True):
    walkthrough_acts = []
    if args.walk_acts:
        walkthrough_acts_path = f"{args.output_dir}/{args.game_name}.walkthrough_acts"
        if os.path.exists(walkthrough_acts_path):
            # with open(args.walk_acts, "r", encoding="utf-8") as fin:
            with open(
                walkthrough_acts_path,
                "r",
                encoding="utf-8",
            ) as fin:
                for line in fin:
                    # sometimes there are void action, use whatever after ":"
                    act = line.split(":")[1].strip()
                    walkthrough_acts.append(act)
            print(
                f"Walkthrough Acts provided has been loaded, total {len(walkthrough_acts)} steps"
            )
        else:
            # walkthrough
            walkthrough_acts = env.get_walkthrough()
    else:
        # walkthrough
        walkthrough_acts = env.get_walkthrough()
    if keep_again:
        walkthrough_acts = __process_again(walkthrough_acts)
    return walkthrough_acts


# ============================= not used =============================


def load_code2anno(input_file_path):
    # object id --> anno str
    with open(input_file_path, "r", encoding="utf-8") as fin:
        code2anno_dict = json.load(fin)

    return_dict = {}
    pattern = r"\(obj(\d+)\)"
    for key in code2anno_dict.keys():
        match = re.search(pattern, key)
        assert match
        obj_number = int(match.group(1))
        return_dict[obj_number] = code2anno_dict[key]
    return return_dict


def load_code2anno_new(code2anno_path):
    assert os.path.exists(code2anno_path)
    with open(code2anno_path, "r", encoding="utf-8") as f:
        code2anno_dict = json.load(f)

    # process to speed up query
    for code in code2anno_dict.keys():
        anno = code2anno_dict[
            code
        ]  # this may be 1. anno str, 2. a dict of {anno str: [[step, position], ...]
    if isinstance(anno, dict):
        # create revert link map, from {anno str: [[step, position], ...]} --> {(step, position): anno str, ...}
        anno_dict = anno
        revert_dict = {}
        for anno in anno_dict.keys():
            for entry in anno_dict[anno]:
                # map both entry element to str
                revert_dict[(str(entry[0]), str(entry[1]))] = anno
        code2anno_dict[code] = revert_dict
    return code2anno_dict


def code2anno_decode(code2anno_dict, code: str, step_num: str, position: str):
    if code not in code2anno_dict.keys():
        return None
    anno = code2anno_dict[
        code
    ]  # this may be 1. anno str, 2. a dict of {anno str: [[step, position], ...]}
    if isinstance(anno, str):  # very luck :)
        return anno
    elif isinstance(anno, dict):  # not bad :|
        anno_dict = anno
        entry = (step_num, position)
        if entry in anno_dict:
            return anno_dict[entry]
        else:
            return None
