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


def load_forward_map_nodes(human_map_file_path):
    human_forward_nodes = {}
    with open(human_map_file_path, "r") as f:
        lines_forward = f.readlines()
    for i in range(len(lines_forward)):
        # get step_num and path
        line_forward = lines_forward[i].strip("\ufeff").strip()
        if len(line_forward) == 0:
            continue
        path_forward, step_num_forward = [
            each.strip().lower() for each in line_forward.split(", step")
        ]
        step_num_forward = int(step_num_forward)
        # get src_node, direction, dst_node
        elements_forward = [each.strip().lower() for each in path_forward.split("-->")]
        # print(elements_forward)
        src_node_forward, _, dst_node_forward = elements_forward
        human_forward_nodes[step_num_forward] = (src_node_forward, dst_node_forward)
    return human_forward_nodes


def gen_move_reversed(args):
    game_name = args.game_name
    game_name_raw = game_name.split(".")[0]
    max_steps = args.max_steps
    print("Game: {}, Max steps: {}".format(game_name, max_steps))

    # code2anno dict
    try:
        code2anno_file_path = "{}/{}/{}.code2anno.json".format(
            args.input_dir, game_name_raw, game_name_raw
        )
        codeid2anno_dict = load_code2anno(code2anno_file_path)
        human_map_file_path = "{}/{}/{}.map.human".format(
            args.input_dir, game_name_raw, game_name_raw
        )
        human_forward_nodes = load_forward_map_nodes(human_map_file_path)

    except Exception as e:
        print("code2anno file not existed.", f"Error: {str(e)}", sep="\n")
        return -1

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

    env.reset()
    location_before = env.get_player_location().name.strip().lower()
    location_before_id = env.get_player_location().num

    # create output dir if not exist
    output_dir = args.output_dir + "/" + game_name_raw
    if os.path.exists(output_dir) == False:
        os.makedirs(output_dir)

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

    map_reversed_list = []

    for step_idx, act in enumerate(walkthrough_acts[:max_steps]):
        """
        for each step at step_idx, walk along walkthrough actions until step_idx, then take a reverse attempt
        """
        env.reset()
        location_before = env.get_player_location().name.strip().lower()
        location_before_id = env.get_player_location().num
        for i in range(step_idx):
            env.step(walkthrough_acts[i])
        # get the last location id before step_idx
        should_fall_back_id = env.get_player_location().num

        # take the step_idx-th step
        print(f"at step: {step_idx+1} | action taken: {act}")
        observation, reward, done, info = env.step(act)

        print("observation: {}".format(observation))
        act_unabbrev = unabbreviate(act)
        location_after_id = env.get_player_location().num
        location_after_loc = (
            codeid2anno_dict[location_after_id]
            if location_after_id in codeid2anno_dict
            else "not found"
        )
        print(f"at location: [{location_after_loc}]({location_after_id})")

        # if location_after_id != location_before_id:
        if location_after_id != should_fall_back_id:
            if game_name == "trinity" and location_after_id in TRINITY_STUCK_LOC_ID:
                continue
            if game_name == "sherlock" and location_after_id in SHERLOCK_STUCK_LOC_ID:
                continue

            valid_actions = {unabbreviate(va): va for va in env.get_valid_actions()}
            print(f"current valid actions: {valid_actions}")

            if act_unabbrev in direction_vocab:
                print(f"valid action [{act_unabbrev}]")

                # get the reverse action
                reverse_act = opposite_direction_dict[act_unabbrev]

                # if reverse_act in valid_actions:
                # test each entry of the valid_actions, because some game use phrase like "go back" instead of "back"
                has_reverse_act = False
                jericho_reverse = []
                for va in valid_actions.keys():
                    if reverse_act in va:
                        has_reverse_act = True
                        jericho_reverse.append(valid_actions[va])
                # get the shortest named possible reverse action, to rescue phrases and exact match mixed case
                jericho_reverse = (
                    sorted(jericho_reverse, key=lambda x: len(x))[0]
                    if has_reverse_act
                    else ""
                )

                if has_reverse_act:
                    print(
                        f"valid reverse action [{reverse_act}] == jericho_reverse: {jericho_reverse}"
                    )

                    # step the reverse action
                    observation, reward, done, info = env.step(jericho_reverse)
                    actual_fall_back_id = env.get_player_location().num
                    actual_fall_back_loc = (
                        codeid2anno_dict[actual_fall_back_id]
                        if actual_fall_back_id in codeid2anno_dict
                        else "not found"
                    )
                    should_fall_back_loc = (
                        codeid2anno_dict[should_fall_back_id]
                        if should_fall_back_id in codeid2anno_dict
                        else "not found"
                    )
                    print(
                        f"actual_fall_back_id: [{actual_fall_back_loc}]({actual_fall_back_id}) | should_fall_back_id: [{should_fall_back_loc}]({should_fall_back_id})"
                    )

                    if should_fall_back_id == actual_fall_back_id:
                        print("opposite direction valid: {}".format(reverse_act))
                        desc = "None"
                    else:
                        obsrv_splitted = observation.split("\n")
                        if len(obsrv_splitted) == 1:
                            desc = obsrv_splitted[0]
                        else:
                            desc = "{} || {}".format(
                                obsrv_splitted[0], "".join(obsrv_splitted[1:])
                            )
                else:
                    obsrv_splitted = observation.split("\n")
                    if len(obsrv_splitted) == 1:
                        desc = obsrv_splitted[0]
                    else:
                        desc = "{} || {}".format(
                            obsrv_splitted[0], "".join(obsrv_splitted[1:])
                        )
                try:
                    map_reversed_list.append(
                        {
                            "location_before": codeid2anno_dict[location_after_id],
                            "location_before_id": location_after_id,
                            "act": reverse_act,
                            "location_after": codeid2anno_dict[should_fall_back_id],
                            "location_after_id": should_fall_back_id,
                            "step_num": step_idx + 1,
                            "desc": desc,
                        }
                    )
                except Exception as e:
                    print(e)
                    print(observation)
                    print(location_after_id)
                    print(codeid2anno_dict)
            location_before_id = location_after_id
            print("================")


    output_file = "{}/{}.map.reversed".format(output_dir, game_name_raw)
    with open(output_file, "w", encoding="utf-8") as fout:
        for item in map_reversed_list:
            if item["act"] != None and item["step_num"] in human_forward_nodes:
                # human forward map: src_node --> direction --> dst_node
                # reversed map: dst_node --> opposite_direction --> src_node
                # as long as the conflict is deem resolved, the entries from human and machine should have the same set of nodes, whenever the step_num is the same
                if not (
                    item["location_before"].strip().lower()
                    == human_forward_nodes[item["step_num"]][1]
                    and item["location_after"].strip().lower()
                    == human_forward_nodes[item["step_num"]][0]
                ):
                    print(
                        f"step_num: {item['step_num']} is not good",
                        f"human forward nodes: {human_forward_nodes[item['step_num']]}",
                        f"machine reversed nodes: {(item['location_before'], item['location_after'])}",
                        sep="\n",
                    )
                    continue
                # assert (
                #     item["location_before"].strip().lower()
                #     == human_forward_nodes[item["step_num"]][1]
                #     and item["location_after"].strip().lower()
                #     == human_forward_nodes[item["step_num"]][0]
                # ), f"step_num: {item['step_num']} is not good, human forward nodes: {human_forward_nodes[item['step_num']]}, machine reversed nodes: {(item['location_before'], item['location_after'])}\nALERT: [gen_move_merge.py might be ran already]"
                print(
                    f"step_num: {item['step_num']} is good",
                    f"human forward nodes: {human_forward_nodes[item['step_num']]}",
                    f"machine reversed nodes: {(item['location_before'], item['location_after'])}",
                    sep="\n",
                )
                fout.write(
                    "{} (obj{}) --> {} --> {} (obj{}), step {}, desc: {}\n".format(
                        item["location_before"],
                        item["location_before_id"],
                        item["act"],
                        item["location_after"],
                        item["location_after_id"],
                        item["step_num"],
                        item["desc"],
                    )
                )
            # else:
            #     fout.write('\n')
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
    gen_move_reversed(args)
