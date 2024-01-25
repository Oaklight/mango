import sys
import argparse
import os

from jericho.util import unabbreviate

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from gen_moves.utils import (
    direction_vocab,
    direction_vocab_abbrv,
    load_env,
    load_walkthrough_acts,
)


def gen_move_machine(args):
    # env
    # env = FrotzEnv("{}/{}".format(args.jericho_path, game_name))
    env = load_env(args)

    env.reset()
    location_before = env.get_player_location().name.strip().lower()
    location_before_id = env.get_player_location().num

    # use provided walkthrough_acts or load from game env
    walkthrough_acts = load_walkthrough_acts(args, env)

    if args.max_steps == -1:
        args.max_steps = len(walkthrough_acts)
    print("Game: {}, Max steps: {}".format(args.game_name, args.max_steps))

    map_list = []
    move_list = []

    valid_acts = walkthrough_acts[: args.max_steps]

    for step_idx, act in enumerate(valid_acts):
        observation, reward, done, info = env.step(act)
        # print(step_idx, act, env.get_player_location())
        try:
            location_after = env.get_player_location().name.strip().lower()
        except:
            print(
                "{}||{}||{}||{}||{}||{}".format(
                    step_idx, act, observation, reward, done, info
                )
            )
            location_after = None
            # exit(0)

        location_after_id = env.get_player_location().num

        # any of the following conditions are met, we consider it a move
        # some move will result in "you can't go" similar words in observation
        conditions = [
            location_after_id != location_before_id,
            unabbreviate(act) in direction_vocab and not "can't" in observation,
            act in direction_vocab_abbrv and not "can't" in observation,
        ]
        if any(conditions):
            map_list.append(
                {
                    "location_before": location_before,
                    "location_before_id": location_before_id,
                    "act": unabbreviate(act),
                    "location_after": location_after,
                    "location_after_id": location_after_id,
                    "step_num": step_idx + 1,
                }
            )
            move_list.append(unabbreviate(act))

            location_before = location_after
            location_before_id = location_after_id

            # print(step_idx, unabbreviate(act), act)

    if len(map_list) == 0:
        print("No map generated!")
        exit(-1)
    print(f"{len(map_list)} edges are valid")

    output_file = f"{args.output_dir}/{args.game_name_raw}.map.machine"
    with open(output_file, "w", encoding="utf-8") as fout:
        for item in map_list:
            fout.write(
                "{} (obj{}) --> {} --> {} (obj{}), step {}\n".format(
                    item["location_before"],
                    item["location_before_id"],
                    item["act"],
                    item["location_after"],
                    item["location_after_id"],
                    item["step_num"],
                )
            )
    print("Saved to {}".format(output_file))

    output_file = f"{args.output_dir}/{args.game_name_raw}.moves"
    valid_moves = list(set(move_list).union(set(direction_vocab)))
    # sort valid_moves by str content
    valid_moves = sorted(valid_moves, key=lambda x: str(x))
    with open(output_file, "w", encoding="utf-8") as fout:
        for sample in valid_moves:
            fout.write("{}\n".format(sample))
    print("Saved to {}".format(output_file))


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
    gen_move_machine(args)
