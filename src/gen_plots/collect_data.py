# this function of this script is to collect plotting model performance data from evals folder
# evals has folders for each model
# under each folder, there are two task folder: desti (for destination finding task) and route (for route finding task)
# under each task folder, there are 53 game folders
# each game folder has a json file for "harsh" eval and a json file for "nice" eval

import csv
import json
import argparse
import os
import sys

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from gen_paths.utils import print_color

EVAL_DIR = ""
TEMP_DIR = ""


def collect_data(eval_dir, temp_dir):
    EVAL_DIR = os.path.abspath(eval_dir)
    TEMP_DIR = os.path.abspath(temp_dir)
    # replace TEMP_DIR with new TEMP_DIR
    if os.path.exists(TEMP_DIR):
        os.system(f"rm -rf {TEMP_DIR}")
    os.makedirs(TEMP_DIR)

    assert os.path.exists(EVAL_DIR), "eval folder does not exist!"

    # get all available model names, and create folder in temp for each model
    # model_names = os.listdir(EVAL_DIR) exclude non-folder stuffs
    model_names = [
        each for each in os.listdir(EVAL_DIR) if os.path.isdir(f"{EVAL_DIR}/{each}")
    ]
    model_names.sort(reverse=True)
    for model_name in model_names:
        if not os.path.exists(f"{TEMP_DIR}/{model_name}"):
            os.makedirs(f"{TEMP_DIR}/{model_name}")

    # for desti folder, create a desti.nice.json and desti.harsh.json in temp folder
    # for route folder, create a route.nice.json and route.harsh.json in temp folder

    for model_name in model_names:
        game_acc_desti = {}
        game_acc_route = {}

        model_path = f"{EVAL_DIR}/{model_name}"
        assert os.path.exists(model_path), f"model folder does not exist!: {model_path}"

        task_names = os.listdir(model_path)
        for task_name in task_names:
            avg_acc_nice = 0
            avg_acc_harsh = 0

            task_path = f"{model_path}/{task_name}"
            assert os.path.exists(
                task_path
            ), f"task folder does not exist!: {task_path}"

            # game_names = os.listdir(task_path) # only consider folder
            game_names = [
                each
                for each in os.listdir(task_path)
                if os.path.isdir(f"{task_path}/{each}")
            ]
            print(f"found {len(game_names)} games in {task_name}")
            for game_name in game_names:
                game_path = f"{task_path}/{game_name}"
                assert os.path.exists(
                    game_path
                ), f"game folder does not exist!: {game_path}"

                # get nice and harsh eval json file path
                if task_name == "desti":
                    nice_path = f"{game_path}/destination.nice.json"
                    harsh_path = f"{game_path}/destination.harsh.json"
                elif task_name == "route":
                    nice_path = f"{game_path}/route.nice.json"
                    harsh_path = f"{game_path}/route.harsh.json"
                else:
                    raise ValueError("task name is not valid!")

                # load json file
                nice = json.load(open(nice_path))
                harsh = json.load(open(harsh_path))

                # there should only be one key in nice and harsh, assert this and replace this value into nice and harsh
                assert len(nice.keys()) == 1, "nice json file has more than one key!"
                assert len(harsh.keys()) == 1, "harsh json file has more than one key!"

                nice = nice[list(nice.keys())[0]]
                harsh = harsh[list(harsh.keys())[0]]

                if "desti" in task_name:
                    nice_acc = nice["accuracy_micro"]
                    harsh_acc = harsh["accuracy_micro"]
                    # read "accuracy_micro" from nice and harsh
                    # add to game_acc
                    if game_name not in game_acc_desti:
                        game_acc_desti[game_name] = {}
                    game_acc_desti[game_name]["nice"] = nice_acc
                    game_acc_desti[game_name]["harsh"] = harsh_acc
                elif "route" in task_name:
                    nice_acc = nice["accuracy_macro"]
                    harsh_acc = harsh["accuracy_macro"]
                    # read "accuracy_micro" from nice and harsh
                    # add to game_acc
                    if game_name not in game_acc_route:
                        game_acc_route[game_name] = {}
                    game_acc_route[game_name]["nice"] = nice_acc
                    game_acc_route[game_name]["harsh"] = harsh_acc
                else:
                    raise ValueError("task name is not valid!")
                avg_acc_nice += nice_acc
                avg_acc_harsh += harsh_acc

            # add field of avg acc of nice and hash
            if "desti" in task_name:
                game_acc_desti["avg_nice"] = avg_acc_nice / len(game_names)
                game_acc_desti["avg_harsh"] = avg_acc_harsh / len(game_names)

            elif "route" in task_name:
                game_acc_route["avg_nice"] = avg_acc_nice / len(game_names)
                game_acc_route["avg_harsh"] = avg_acc_harsh / len(game_names)

            # dump game_acc to json file
            json.dump(
                game_acc_desti,
                open(f"{TEMP_DIR}/{model_name}/desti.json", "w"),
                indent=4,
                sort_keys=True,
            )
            json.dump(
                game_acc_route,
                open(f"{TEMP_DIR}/{model_name}/route.json", "w"),
                indent=4,
                sort_keys=True,
            )
        print_color(f"[{model_name}] Eval data collection finished!", "black")

    # dump avg_acc to csv
    # create csv file
    csv_file = open(f"{EVAL_DIR}/avg_acc.csv", "w")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(
        ["model_name", "desti_nice", "desti_harsh", "route_nice", "route_harsh"]
    )
    # for each model, read desti.json and route.json
    # read nice and harsh avg acc
    for model_name in model_names:
        desti = json.load(open(f"{TEMP_DIR}/{model_name}/desti.json"))
        route = json.load(open(f"{TEMP_DIR}/{model_name}/route.json"))
        csv_writer.writerow(
            [
                model_name,
                desti["avg_nice"],
                desti["avg_harsh"],
                route["avg_nice"],
                route["avg_harsh"],
            ]
        )
    csv_file.close()
    print_color(f"avg_acc.csv file created!", "black")


if __name__ == "__main__":
    # argparse to get eval and local folder path
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval_dir", "-e", type=str, default="./evals")
    parser.add_argument("--temp_dir", "-t", type=str, default="./src/gen_plots/data")
    args = parser.parse_args()

    # collect_data(args) use kwarg
    collect_data(eval_dir=args.eval_dir, temp_dir=args.temp_dir)
