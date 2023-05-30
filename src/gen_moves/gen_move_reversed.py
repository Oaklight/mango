import glob
from jericho import *  # https://jericho-py.readthedocs.io/en/latest/index.html
import os
import argparse
from tqdm import tqdm
from jericho import *
from jericho.util import unabbreviate
import json
import re

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
    "up": "up",
    "down": "down",
}


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
        if game_name in game_file:
            game_file_path = game_file
            break
    if game_file_path is None:
        print(f"Game file {game_name} not found in {args.jericho_path}")
        return -1
    env = FrotzEnv(game_file_path)

    env.reset()
    location_before = env.get_player_location().name.strip().lower()
    location_before_id = env.get_player_location().num

    # walkthrough
    walkthrough_acts = env.get_walkthrough()

    map_reversed_list = []
    for step_idx, act in enumerate(walkthrough_acts[:max_steps]):
        observation, reward, done, info = env.step(act)
        act_unabbrev = unabbreviate(act)
        location_after_id = env.get_player_location().num
        if location_after_id != location_before_id:
            valid_actions = [unabbreviate(va) for va in env.get_valid_actions()]
            if act_unabbrev in direction_vocab:
                if opposite_direction_dict[act_unabbrev] in valid_actions:
                    desc = "None"
                else:
                    obsrv_splitted = observation.split("\n")
                    if len(obsrv_splitted) == 1:
                        desc = obsrv_splitted[0]
                    else:
                        desc = "{} || {}".format(
                            obsrv_splitted[0], "".join(obsrv_splitted[1:])
                        )

                map_reversed_list.append(
                    {
                        "location_before": codeid2anno_dict[location_after_id],
                        "location_before_id": location_after_id,
                        "act": opposite_direction_dict[act_unabbrev],
                        "location_after": codeid2anno_dict[location_before_id],
                        "location_after_id": location_before_id,
                        "step_num": step_idx + 1,
                        "desc": desc,
                    }
                )
            location_before_id = location_after_id

    output_dir = args.output_dir + "/" + game_name_raw
    if os.path.exists(output_dir) == False:
        os.makedirs(output_dir)

    output_file = "{}/{}.map.reversed".format(output_dir, game_name_raw)
    with open(output_file, "w", encoding="utf-8") as fout:
        for item in map_reversed_list:
            if item["act"] != None and item["step_num"] in human_forward_nodes:
                # human forward map: src_node --> direction --> dst_node
                # reversed map: dst_node --> opposite_direction --> src_node
                print(
                    f"step_num: {item['step_num']} is good",
                    f"human forward nodes: {human_forward_nodes[item['step_num']]}",
                    f"machine reversed nodes: {(item['location_before'], item['location_after'])}",
                    sep="\n",
                )
                # as long as the conflict is deem resolved, the entries from human and machine should have the same set of nodes, whenever the step_num is the same
                # if (
                #     item["location_before"].strip().lower()
                #     == human_forward_nodes[item["step_num"]][1]
                #     and item["location_after"].strip().lower()
                #     == human_forward_nodes[item["step_num"]][0]
                # ):
                assert (
                    item["location_before"].strip().lower()
                    == human_forward_nodes[item["step_num"]][1]
                    and item["location_after"].strip().lower()
                    == human_forward_nodes[item["step_num"]][0]
                ), f"step_num: {item['step_num']} is not good, human forward nodes: {human_forward_nodes[item['step_num']]}, machine reversed nodes: {(item['location_before'], item['location_after'])}\nALERT: [gen_move_merge.py might be ran already]"
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
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print("Args: {}".format(args))
    gen_move_reversed(args)
