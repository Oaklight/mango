# this function serves to track which node first appears at which step in each game
# this can be extract from game.valid_moves.csv

import json
import os
import sys
import argparse
import pandas as pd

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from gen_paths.gamegraph import anno_to_code

MAP_DIR = "./data/maps"

if __name__ == "__main__":
    # argparse to get MAP_DIR and game name if specified
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--map_dir",
        "-m",
        type=str,
        default=MAP_DIR,
        help="path to the directory containing all the maps",
    )
    parser.add_argument(
        "--game",
        "-g",
        type=str,
        default=None,
        help="game name to extract node-step map",
    )
    parser.add_argument("--max_step", "-s", type=int, default=70)

    args = parser.parse_args()
    MAP_DIR = args.map_dir
    tgt_game = args.game

    # get game name available from infered result dir
    games = [
        f
        for f in os.listdir(MAP_DIR)
        if os.path.isdir(os.path.join(MAP_DIR, f)) and not f.startswith(".")
    ]
    games.sort()
    print(len(games))

    for game in games:
        if tgt_game is not None and game != tgt_game:
            continue

        valid_moves_path = os.path.join(MAP_DIR, game, f"{game}.valid_moves.csv")
        assert os.path.isfile(valid_moves_path), f"{valid_moves_path} not found"

        # load anno2code, if anno2code not found, invalid game, skip
        anno2code = os.path.join(MAP_DIR, game, f"{game}.anno2code.json")
        if not os.path.isfile(anno2code):
            print(f"{anno2code} not found, skip")
            continue
        with open(anno2code, "r") as f:
            anno2code = json.load(f)

        print("============= extracting node-step map ===============")
        print(f"processing {game}")
        # read the valid moves csv, all nodes in "Location Before" and "Location After"
        # use pandas
        # sample header: Step Num,Location Before,Location After,,
        df = pd.read_csv(valid_moves_path)
        # get all nodes in "Location Before" and "Location After"
        node_step = {}
        for i in range(len(df)):
            # skip steps that Location Before and Location After are empty
            if pd.isnull(df["Location Before"][i]) or pd.isnull(
                df["Location After"][i]
            ):
                continue

            step = df["Step Num"][i]
            if step > args.max_step:
                continue

            node_before = df["Location Before"][i].strip()
            node_after = df["Location After"][i].strip()
            # print(step, node_before, node_after)

            node_before_code = anno_to_code(node_before, anno2code)
            node_after_code = anno_to_code(node_after, anno2code)

            if node_before_code not in node_step:
                node_step[node_before_code] = []
            if node_after_code not in node_step:
                node_step[node_after_code] = []

            node_step[node_before_code].append(step)
            node_step[node_after_code].append(step)

        # use min to get the first step that node appears
        for node in node_step:
            node_step[node] = int(min(node_step[node]))

        # assert all anno2code's keys are in node_step
        assert len(anno2code) == len(
            node_step
        ), f"{game} anno2code and node_step not match"

        # write the node_step to json
        with open(os.path.join(MAP_DIR, game, f"{game}.node_step.json"), "w") as f:
            json.dump(node_step, f, indent=4, sort_keys=True)
