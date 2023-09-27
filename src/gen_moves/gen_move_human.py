import argparse
import csv
import glob
import json
import os
from pathlib import Path
from jericho import FrotzEnv
from jericho.util import unabbreviate


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

# argparse to read in annotated walkthrough file, check file extension for either txt or markdown mode
# output valid moves to json file
def walkthrough_annotated_to_valid_moves(walkthrough_file, csv_or_json: str = "csv"):
    if walkthrough_file.endswith(".md"):
        print("markdown mode")
        isMarkdown = True
    else:
        print("txt mode")
        isMarkdown = False
    SECTION_SPLITTER = "***" if isMarkdown else "==========="
    SECTION_HEADER = "# " if isMarkdown else "==>"
    TARGET_HEADER = "## " if isMarkdown else "==>"

    valid_moves = {}
    # read in walkthrough file
    with open(walkthrough_file, "r") as f:
        walkthrough = f.readlines()

        for line in walkthrough:
            # line = line.strip().lower()
            # parse line, skip empty line
            if line == "":
                continue

            # read in step number, check
            if f"{SECTION_HEADER}STEP NUM: " in line:
                step_num = int(line.split(f"{SECTION_HEADER}STEP NUM:")[1])

            if f"{TARGET_HEADER}MOVE: " in line:
                move = line.split(f"{TARGET_HEADER}MOVE:")[1]
                src_node, action, dst_node = [
                    each.strip().lower() for each in move.split("-->")
                ]
                valid_moves[step_num] = {
                    "src_node": src_node,
                    "action": action,
                    "dst_node": dst_node,
                }
                print(
                    f"FOUND valid move [{step_num}]: {src_node} --> {action} --> {dst_node}"
                )

    print(f"{len(valid_moves)} valid moves found in {walkthrough_file}")
    # dump valid moves to json file
    # output file name is game.valid_moves.json, game is part of walkthrough_file, in md mode, game.walkthrough.md, in txt mode, game.walkthrough
    if csv_or_json == "csv":
        output_file = walkthrough_file.split(".walkthrough")[0] + ".valid_moves.csv"
        with open(output_file, "w") as f:
            f.write("Step Num, Location Before, Location After\n")
            # write lines starting with step number, regardless of whether it's in valid_moves
            for i in range(step_num):
                if i == 0:
                    continue
                if i in valid_moves:
                    f.write(
                        f"{i}, {valid_moves[i]['src_node']}, {valid_moves[i]['dst_node']}\n"
                    )
                else:
                    f.write(f"{i}, , \n")

    elif csv_or_json == "json":
        output_file = walkthrough_file.split(".walkthrough")[0] + ".valid_moves.json"
        with open(output_file, "w") as f:
            json.dump(valid_moves, f, indent=4)
    else:
        raise NotImplementedError
    print(f"Valid moves written to {output_file}")

    return valid_moves


def read_csv(path_in, max_steps=70):
    print("Reading file {} ing ...".format(path_in))
    valid_moves = {}
    with open(path_in, "r", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file)
        header = next(csv_reader)
        step_num_idx = header.index("Step Num")
        location_before_idx = header.index("Location Before")
        location_after_idx = header.index("Location After")
        for i, row in enumerate(csv_reader):
            if i == max_steps:
                break
            step_num = row[step_num_idx].strip()
            location_before = row[location_before_idx].strip()
            location_after = row[location_after_idx].strip()
            valid_move = location_before != ""
            valid_moves[step_num] = {
                "step_num": step_num,
                "src_node": location_before,
                "dst_node": location_after,
                "valid_move": valid_move,
            }
    print("Done.")
    return valid_moves


def generate_move_human(valid_moves: dict, jericho_path, game_name, output_dir, max_steps):
    # get files in jericho_path, one of game_name.z3 or game_name.z5 or game_name.z8 must exist
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

    # walkthrough
    walkthrough = env.get_walkthrough()
    walkthrough = [
        direction_abbrv_dict[item.lower()]
        if item.lower() in direction_vocab_abbrv
        else unabbreviate(item).lower()
        for item in walkthrough
    ]

    max_steps = min(len(walkthrough), max_steps)
    print("Game: {}, Max steps: {}".format(game_name, max_steps))

    # convert valid_moves to list, sorted by step number, int
    valid_moves = [
        valid_moves[key] for key in sorted(valid_moves.keys(), key=lambda x: int(x))
    ]
    valid_moves = valid_moves[:max_steps]
    print(len(valid_moves))

    # annotated valid moves
    output_file = "{}/{}.map.human".format(output_dir, game_name)
    with open(output_file, "w", encoding="utf-8") as fout:
        for step_idx, move in enumerate(valid_moves):
            try:
                move["act"] = walkthrough[step_idx]
            except Exception as e:
                print(e)
                print(
                    "step_idx: {}, len(walkthrough): {}".format(
                        step_idx, len(walkthrough)
                    )
                )
            if move["valid_move"]:
                fout.write(
                    "{} --> {} --> {}, step {}\n".format(
                        move["src_node"],
                        move["act"],
                        move["dst_node"],
                        move["step_num"],
                    )
                )
                # print(step_idx, move["act"])
    print("Saved to {}".format(output_file))
    print("Good Job!")


def get_args():
    parser = argparse.ArgumentParser()
    # walkthrough_file, valid_move_csv as mutually exclusive
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--walkthrough_file", "-w", type=str, default=None)
    group.add_argument("--valid_move_csv", "-c", type=str, default=None)

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
    args = parser.parse_args()
    # output_dir is the same folder as walkthrough_file: ../../data/maps/omniquest/omniquest.valid_moves.csv
    # if walkthrough_file is not provided, then output_dir is the same folder as valid_move_csv
    if args.walkthrough_file:
        args.output_dir = "/".join(args.walkthrough_file.split("/")[:-1])
        args.game_name = args.walkthrough_file.split("/")[-1].split(".")[0]
    else:
        args.output_dir = "/".join(args.valid_move_csv.split("/")[:-1])
        args.game_name = args.valid_move_csv.split("/")[-1].split(".")[0]
    return args


if __name__ == "__main__":
    args = get_args()

    if args.valid_move_csv:
        valid_moves = read_csv(args.valid_move_csv, args.max_step)
    else:
        valid_moves = walkthrough_annotated_to_valid_moves(args.walkthrough_file)

    # jericho_path_for_game = args.jericho_path + '/' + args.game_name + '.z5'
    generate_move_human(valid_moves, args.jericho_path, args.game_name, args.output_dir, args.max_step)
