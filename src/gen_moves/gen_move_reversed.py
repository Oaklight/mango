import argparse
import os
import sys

from tqdm import tqdm
from jericho import *
from jericho.util import unabbreviate

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from gen_moves.utils import load_env, load_walkthrough_acts

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


def load_forward_map_nodes(human_map_path):
    assert os.path.exists(human_map_path)
    with open(human_map_path, "r") as f:
        lines_forward = f.readlines()

    human_forward_edges = {}
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
        human_forward_edges[step_num] = tuple(elements_forward)
    return human_forward_edges


def get_potential_reverse_edges(human_forward_edges, max_steps):
    # unabbreviate all act and get all directional forward edges
    forward_directional_edges = {
        step_num: (edge[0], unabbreviate(edge[1]), edge[2])
        for step_num, edge in human_forward_edges.items()
        if unabbreviate(edge[1]) in direction_vocab and step_num <= max_steps
    }

    potential_reverse_directional_edges = {}
    needs_jericho_check = []
    confirm_jericho_valid = []

    for step_num, edge in forward_directional_edges.items():
        src_anno, act, dst_anno = edge
        act_revert = opposite_direction_dict[act]
        reverse_edge = (dst_anno, act_revert, src_anno)

        potential_reverse_directional_edges[step_num] = reverse_edge
        if reverse_edge in forward_directional_edges.values():
            # appeared in forward directional edge, it's valid by default.
            confirm_jericho_valid.append(step_num)
        else:
            needs_jericho_check.append(step_num)
    assert len(set(confirm_jericho_valid).intersection(set(needs_jericho_check))) == 0
    return (
        potential_reverse_directional_edges,
        needs_jericho_check,
        confirm_jericho_valid,
    )


def gen_move_reversed(args):
    env = load_env(args)
    # use provided walkthrough_acts or load from game env
    walkthrough_acts = load_walkthrough_acts(args, env)

    if args.max_steps == -1:
        args.max_steps = len(walkthrough_acts)
    print(f"Game: {args.game_name}, Max steps: {args.max_steps}")

    # load all necessary files
    human_map_file_path = (
        f"{args.input_dir}/{args.game_name_raw}/{args.game_name_raw}.map.human"
    )
    human_forward_edges = load_forward_map_nodes(human_map_file_path)
    (
        potential_reverse_directional_edges,
        needs_jericho_check,
        confirm_jericho_valid,
    ) = get_potential_reverse_edges(human_forward_edges, args.max_steps)
    print(f"ATTENTION | {len(needs_jericho_check)} potential reverse edges to check!")

    # for step_idx, act in enumerate(walkthrough_acts[:max_steps]):
    for step_num in tqdm(needs_jericho_check, leave=None):
        """
        for each step at needs_jericho_check, walk along walkthrough actions until step_idx, then take a reverse attempt
        """

        step_idx = step_num - 1

        act = walkthrough_acts[step_idx]
        act = unabbreviate(act)
        act_revert = opposite_direction_dict[act]

        # reset the game env and simulate act until step_idx
        env.reset()
        halt_flag = False

        for i in range(step_idx):
            env.step(walkthrough_acts[i])
            if env._emulator_halted():
                halt_flag = True
                break
        if halt_flag:
            print(f"HALT || @{step_num}, [{act}] halt the jericho engine.")
            continue

        # location id AT step_idx-1
        location_before = env.get_player_location().name.strip().lower()
        location_before_id = env.get_player_location().num
        should_fallback_code = f"{location_before} (obj{location_before_id})".strip()

        # take the step_idx-th step
        env.step(act)
        if env._emulator_halted():
            halt_flag = True
            print(f"HALT || @{step_num}, [{act}] reverse the jericho engine.")
            continue

        # location id AT step_idx
        location_now = env.get_player_location().name.strip().lower()
        location_now_id = env.get_player_location().num
        arrive_code = f"{location_now} (obj{location_now_id})".strip()

        print(f"@{step_num} | [{should_fallback_code}] --> {act} --> [{arrive_code}]")

        # if game_name == "trinity" and location_now_id in TRINITY_STUCK_LOC_ID:
        #     continue
        # if game_name == "sherlock" and location_now_id in SHERLOCK_STUCK_LOC_ID:
        #     continue

        # attempt to reverse the action
        # check if reverse action is a valid option?
        valid_act_reverts = [unabbreviate(va) for va in env.get_valid_actions()]
        if act_revert not in valid_act_reverts:
            print(
                f"NON-VALID-ACTION || reverse[{act}] = [{act_revert}], but it's not a valid action @{step_num}."
            )
            continue
        else:
            # take the reverse step
            env.step(act_revert)
            if env._emulator_halted():
                halt_flag = True
                print(
                    f"HALT || @{step_num}, [{act_revert}] reverse the jericho engine."
                )
                continue

            # location id AT step_num's revert
            location_after = env.get_player_location().name.strip().lower()
            location_after_id = env.get_player_location().num
            actual_fallback_code = f"{location_after} (obj{location_after_id})".strip()

            if actual_fallback_code == should_fallback_code:
                print(
                    f"VALID || @{step_num}, {should_fallback_code} --> {act} --> [{arrive_code}] --> {act_revert} --> {actual_fallback_code}"
                )
                confirm_jericho_valid.append(step_num)

            else:
                print(
                    f"INVALID || @{step_num}, {should_fallback_code} --> {act} --> [{arrive_code}] -x-> {act_revert} -x-> [{should_fallback_code}]"
                )

            print(f"================ done with {step_num} ================")

    # add to confirmed_reverse_directional_edges
    confirmed_reverse_directional_edges = []
    for valid_step_num in confirm_jericho_valid:
        (src_anno, act_revert, dst_anno) = potential_reverse_directional_edges[
            valid_step_num
        ]
        confirmed_reverse_directional_edges.append(
            {
                "step_num": valid_step_num,
                "act_revert": act_revert,
                "src": src_anno,
                "dst": dst_anno,
            }
        )

    output_file = f"{args.output_dir}/{args.game_name_raw}.map.reversed"
    with open(output_file, "w", encoding="utf-8") as fout:
        for item in confirmed_reverse_directional_edges:
            fout.write(
                "{} --> {} --> {}, step {}, desc: None\n".format(
                    item["src"], item["act_revert"], item["dst"], item["step_num"]
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
    args = parser.parse_args()

    args.game_name_raw = args.game_name.split(".")[0]
    args.output_dir = f"{args.output_dir}/{args.game_name_raw}"

    # create output dir if not exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    return args


if __name__ == "__main__":
    args = parse_args()
    print("Args: {}".format(args))
    print()
    print()
    print("++++++++++++++++++++++++++++++++++")
    print(args.game_name)
    print("++++++++++++++++++++++++++++++++++")

    # if args.game_name in ["sherlock", "trinity"]:
    #     exit(-1)
    gen_move_reversed(args)
