import argparse
import os

import pandas

abbr_dict = {
    "w": "west",
    "e": "east",
    "s": "south",
    "n": "north",
    "nw": "northwest",
    "ne": "northeast",
    "sw": "southwest",
    "se": "southeast",
    'd': 'down',
    'u': 'up',
}


def unabbreviate_actions(action):
    if action in abbr_dict:
        return abbr_dict[action]
    else:
        return action


def parse_args():
    parser = argparse.ArgumentParser(description="Extract actions from csv")
    parser.add_argument(
        "--output_dir",
        "-o",
        type=str,
        default="./data-intermediate",
        help="output directory",
    )
    parser.add_argument("--game_name", "-g", type=str, help="game name", required=True)

    args = parser.parse_args()
    args.game_dir = os.path.join(args.output_dir, args.game_name)
    args.walkthrough_actions_file = os.path.join(
        args.game_dir, f"{args.game_name}.walkthrough_acts"
    )
    args.csv_file = os.path.join(args.game_dir, f"{args.game_name}.valid_moves.csv")

    return args


def extract_actions(walkthrough_actions_file):
    with open(walkthrough_actions_file) as f:
        lines = f.readlines()
        actions = [unabbreviate_actions(line.split(":")[1].strip().lower()) for line in lines]

    return actions


def insert_actions(csv_file, actions):
    df = pandas.read_csv(csv_file, header=0)
    df["taken_action"] = actions
    df.to_csv(csv_file, index=False)


if __name__ == "__main__":
    args = parse_args()
    actions = extract_actions(args.walkthrough_actions_file)
    insert_actions(args.csv_file, actions)
