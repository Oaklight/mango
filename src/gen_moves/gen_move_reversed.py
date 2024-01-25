import glob
import sys
from jericho import *  # https://jericho-py.readthedocs.io/en/latest/index.html
import os
import argparse
from tqdm import tqdm
from jericho import *
from jericho.util import unabbreviate
import json
import re

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from gen_moves.utils import process_again

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

# post issues at jericho repo: https://github.com/microsoft/jericho/issues/64
TRINITY_STUCK_STEPS = (8, 13, 23, 29, 33, 35, 39, 43, 47, 49, 58, 59, 60, 65, 68, 69)
TRINITY_STUCK_LOC_ID = (79, 354, 144, 355, 531, 179, 371, 121, 438, 576, 323, 319, 575, 80, 316)
SHERLOCK_STUCK_LOC_ID = (111, 3, 37, 33, 93, 71, 5, 73, 1, 85, 295, 52, 57, 21, 69, 27, 12)


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


def load_forward_map_nodes(human_map_path):
    assert os.path.exists(human_map_path)
    with open(human_map_path, "r") as f:
        lines_forward = f.readlines()

    human_forward_nodes = {}
    for line in lines_forward:
        # get step_num and path
        line = line.strip("\ufeff").strip()
        if len(line) == 0:
            continue

        path_forward, step_num = [each.strip() for each in line.split(", step")]
        step_num = int(step_num)

        # get src_node, direction, dst_node
        elements_forward = [each.strip() for each in path_forward.split("-->")]
        # print(elements_forward)
        human_forward_nodes[step_num] = tuple(elements_forward)
    return human_forward_nodes


def gen_move_reversed(args):
    game_name = args.game_name
    game_name_raw = game_name.split(".")[0]
    max_steps = args.max_steps

    # create output dir if not exist
    output_dir = f"{args.output_dir}/{game_name_raw}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # code2anno dict
    code2anno_file_path = (
        f"{args.input_dir}/{game_name_raw}/{game_name_raw}.code2anno.json"
    )
    code2anno_dict = load_code2anno_new(code2anno_file_path)

    human_map_file_path = f"{args.input_dir}/{game_name_raw}/{game_name_raw}.map.human"
    human_forward_nodes = load_forward_map_nodes(human_map_file_path)

    machine_map_file_path = (
        f"{args.input_dir}/{game_name_raw}/{game_name_raw}.map.machine"
    )
    machine_forward_nodes = set(load_forward_map_nodes(machine_map_file_path).values())

    # env
    # search for game_name in jericho_path. The real game file should be game_name.z3 or .z5 or .z8
    # by cross checking with entries in glob
    game_file_path = None
    for game_file in glob.glob(f"{args.jericho_path}/*"):
        if game_name == os.path.splitext(os.path.basename(game_file))[0]:
            game_file_path = game_file
            break
    if game_file_path is None:
        print(f"Game file {game_name} not found in {args.jericho_path}")
        return -1
    env = FrotzEnv(game_file_path)

    # use provided walkthrough_acts or load from game env
    walkthrough_acts = []
    if args.walk_acts:
        # with open(args.walk_acts, "r", encoding="utf-8") as fin:
        with open(
            f"{output_dir}/{game_name}.walkthrough_acts", "r", encoding="utf-8"
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
    walkthrough_acts = process_again(walkthrough_acts)

    if max_steps == -1:
        max_steps = len(walkthrough_acts)
    print(f"Game: {game_name}, Max steps: {max_steps}")

    map_reversed_list = []
    for step_idx, act in enumerate(walkthrough_acts[:max_steps]):
        halt_flag = False
        """
        for each step at step_idx, walk along walkthrough actions until step_idx, then take a reverse attempt
        """
        # if step_idx+1 not in human_map, then we can forget it :)
        if step_idx + 1 not in human_forward_nodes.keys():
            print(f"SKIPPING || @{step_idx+1}, [{act}] is not in the human map.")
            continue

        # first we should check if the "act" is one of the directional one? if not we can skip the entire check at this step
        act = unabbreviate(act)
        if act not in direction_vocab:
            print(f"SKIPPING || @{step_idx+1}, [{act}] is not a directional move.")
            continue
        else:
            act_revert = opposite_direction_dict[act]

        # reset the game env and simulate act until step_idx
        env.reset()

        for i in range(step_idx):
            env.step(walkthrough_acts[i])
            if env._emulator_halted():
                halt_flag = True

                break
        if halt_flag:
            print(f"HALT || @{step_idx+1}, [{act}] halt the jericho engine.")
            continue

        # location id AT step_idx-1
        location_before = env.get_player_location().name.strip().lower()
        location_before_id = env.get_player_location().num
        should_fallback_code = f"{location_before} (obj{location_before_id})".strip()

        # take the step_idx-th step
        env.step(act)
        if env._emulator_halted():
            halt_flag = True
            print(f"HALT || @{step_idx+1}, [{act}] reverse the jericho engine.")
            continue

        # location id AT step_idx
        location_now = env.get_player_location().name.strip().lower()
        location_now_id = env.get_player_location().num
        arrive_code = f"{location_now} (obj{location_now_id})".strip()

        print(f"@{step_idx+1} | [{should_fallback_code}] --> {act} --> [{arrive_code}]")

        # if game_name == "trinity" and location_now_id in TRINITY_STUCK_LOC_ID:
        #     continue
        # if game_name == "sherlock" and location_now_id in SHERLOCK_STUCK_LOC_ID:
        #     continue

        # attempt to reverse the action

        # check if reverse action is a valid option?
        valid_act_reverts = [unabbreviate(va) for va in env.get_valid_actions()]
        if act_revert not in valid_act_reverts:
            print(
                f"SKIPPING || reverse[{act}] = [{act_revert}], but it's not a valid action @{step_idx+1}."
            )
            continue
        else:
            # take the reverse step
            env.step(act_revert)
            if env._emulator_halted():
                halt_flag = True
                print(
                    f"HALT || @{step_idx+1}, [{act_revert}] reverse the jericho engine."
                )
                continue

            # location id AT step_idx+1's revert
            location_after = env.get_player_location().name.strip().lower()
            location_after_id = env.get_player_location().num
            actual_fallback_code = f"{location_after} (obj{location_after_id})".strip()

            if actual_fallback_code == should_fallback_code:
                # check if (arrive_code, act_revert, actual_fallback_code) in machine forward map
                if (
                    arrive_code,
                    act_revert,
                    actual_fallback_code,
                ) in machine_forward_nodes:
                    print(
                        f"HIT || [{arrive_code} --> {act_revert} --> {actual_fallback_code}] already in the machine forward map"
                    )
                    continue

                else:
                    # `act` is a revertable move
                    print(
                        f"VALID || @{step_idx+1}, {should_fallback_code} --> {act} --> {arrive_code} <-- {act_revert} <-- {actual_fallback_code}"
                    )
                    # add to map_reversed_list
                    map_reversed_list.append(
                        {
                            "step_num": step_idx + 1,
                            "act": act,
                            "act_revert": act_revert,
                            "location_before": location_before,
                            "location_before_id": location_before_id,
                            "location_now": location_now,
                            "location_now_id": location_now_id,
                        }
                    )
            else:
                print(
                    f"INVALID || @{step_idx+1}, {should_fallback_code} --> {act} --> {arrive_code} <-- {act_revert} <-- [{actual_fallback_code}]"
                )

            print(f"================ done with {step_idx+1} ================")

    output_file = "{}/{}.map.reversed".format(output_dir, game_name_raw)
    with open(output_file, "w", encoding="utf-8") as fout:
        for item in map_reversed_list:
            fout.write(
                "{} (obj{}) --> {} --> {} (obj{}), step {}, desc: None\n".format(
                    item["location_now"],
                    item["location_now_id"],
                    item["act_revert"],
                    item["location_before"],
                    item["location_before_id"],
                    item["step_num"],
                )
            )

    print("Good Job!")
    return 0


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--game_name", "-g", type=str)
    parser.add_argument(
        "--jericho_path",
        "-j",
        type=str,
        default="./data/z-machine-games-master/jericho-game-suite",
    )
    parser.add_argument("--max_steps", type=int, default=70)
    parser.add_argument("--input_dir", "-idir", type=str, default="./data/maps")
    parser.add_argument("--output_dir", "-odir", type=str, default="./data/maps")
    parser.add_argument(
        "--walk_acts",
        "-acts",
        action="store_true",
        default=False,
        help="Override walkthrough acts with *.walkthrough_acts file",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print("Args: {}".format(args))
    print()
    print()
    print("++++++++++++++++++++++++++++++++++")
    print(args.game_name)
    print("++++++++++++++++++++++++++++++++++")

    if args.game_name in ["sherlock", "trinity"]:
        exit(-1)
    gen_move_reversed(args)
