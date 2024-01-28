import argparse
import csv
import json
import os
import sys

from jericho.util import unabbreviate

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from gen_moves.utils import (
    direction_abbrv_dict,
    direction_vocab_abbrv,
    load_env,
    load_walkthrough_acts,
)


def read_csv(path_in, max_steps=70):
    print("Reading file {} ing ...".format(path_in))
    valid_moves = {}
    with open(path_in, "r", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file)
        header = next(csv_reader)
        step_num_idx = header.index("Step Num")
        location_before_idx = header.index("Location Before")
        location_after_idx = header.index("Location After")

        if "Answerable" in header:
            answerable_idx = header.index("Answerable")
        else:
            answerable_idx = header.index("Step Num")

        for i, row in enumerate(csv_reader):
            if i == max_steps:
                break
            step_num = row[step_num_idx].strip()
            location_before = row[location_before_idx].strip()
            location_after = row[location_after_idx].strip()
            valid_move = location_before != ""

            answerable = row[answerable_idx].strip()
            if answerable == "":
                answerable = step_num

            valid_moves[step_num] = {
                "step_num": step_num,
                "src_node": location_before,
                "dst_node": location_after,
                "valid_move": valid_move,
                "answerable": answerable,
            }
    print("Done.")
    return valid_moves


def generate_move_human(valid_moves: dict, game_name, output_dir, max_steps):
    # get files in jericho_path, one of game_name.z3 or game_name.z5 or game_name.z8 must exist
    env = load_env(args)

    env.reset()

    # use provided walkthrough_acts or load from game env
    walkthrough_acts = load_walkthrough_acts(args, env)
    if max_steps == -1:
        max_steps = len(walkthrough_acts)
    max_steps = min(len(walkthrough_acts), max_steps)
    print("Game: {}, Max steps: {}".format(game_name, max_steps))

    # get all unabbreviated action term. if it's not unabbreviateable, use lowercased original.
    walkthrough_acts = [
        direction_abbrv_dict[item.lower()]
        if item.lower() in direction_vocab_abbrv
        else unabbreviate(item).lower()
        for item in walkthrough_acts
    ]

    # convert valid_moves to list, sorted by step number, int
    valid_moves = [
        valid_moves[key] for key in sorted(valid_moves.keys(), key=lambda x: int(x))
    ]
    valid_moves = valid_moves[:max_steps]
    print(len(valid_moves))

    # annotated valid moves
    output_file = f"{output_dir}/{game_name}.map.human"
    with open(output_file, "w", encoding="utf-8") as fout:
        for step_idx, move in enumerate(valid_moves):
            try:
                move["act"] = walkthrough_acts[step_idx]
            except Exception as e:
                print(e)
                print(
                    "step_idx: {}, len(walkthrough_acts): {}".format(
                        step_idx, len(walkthrough_acts)
                    )
                )
            if move["valid_move"]:
                fout.write(
                    "{} --> {} --> {}, step {}, answerable {}\n".format(
                        move["src_node"],
                        move["act"],
                        move["dst_node"],
                        int(move["step_num"]),
                        int(move["answerable"]),
                    )
                )
                # print(step_idx, move["act"])
    print("Saved to {}".format(output_file))
    print("Good Job!")


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--valid_move_csv", "-c", type=str, default=None, required=True)
    parser.add_argument(
        "--jericho_path",
        "-j",
        type=str,
        default="z-machine-games-master/jericho-game-suite",
    )
    parser.add_argument(
        "--max_step",
        "-s",
        type=int,
        default=70,
    )
    parser.add_argument(
        "--walk_acts",
        "-acts",
        action="store_true",
        default=False,
        help="Override walkthrough acts with *.walkthrough_acts file",
    )
    args = parser.parse_args()
    # output_dir is the same folder as valid_moves.csv: ../../data/maps/omniquest/omniquest.valid_moves.csv
    args.output_dir = "/".join(args.valid_move_csv.split("/")[:-1])
    args.game_name = args.valid_move_csv.split("/")[-1].split(".")[0]

    return args


if __name__ == "__main__":
    args = get_args()

    valid_moves = read_csv(args.valid_move_csv, args.max_step)

    # jericho_path_for_game = args.jericho_path + '/' + args.game_name + '.z5'
    generate_move_human(valid_moves, args.game_name, args.output_dir, args.max_step)
