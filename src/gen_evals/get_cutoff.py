# this function serves to read off cutoff step from fjd's infered data

import argparse
import json
import os

INFER_DIR = "../mango-inhouse-llms/llama"
EVAL_DIR = "./evals_llama"


# read off cutoff step from fjd's infered data
def get_cutoff(gpt_result_json):
    # load the json and read off the config field
    with open(gpt_result_json, "r") as f:
        data = json.load(f)
    return data["cut_off_num"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--infer_dir", "-i", type=str, required=True)
    parser.add_argument("--eval_dir", "-e", type=str, required=True)
    parser.add_argument("--task_name", "-t", type=str, required=True)
    parser.add_argument("--model_name", "-m", type=str, required=True)
    args = parser.parse_args()
    EVAL_DIR = args.eval_dir
    INFER_DIR = args.infer_dir
    # create if eval dir doesn't exist
    if not os.path.exists(EVAL_DIR):
        os.makedirs(EVAL_DIR)

    cutoff_step = {}

    # get game name available from infered result dir
    games = [
        f
        for f in os.listdir(INFER_DIR)
        if os.path.isdir(os.path.join(INFER_DIR, f)) and not f.startswith(".")
    ]
    print(len(games))

    for game in games:
        result_sample_path = os.path.join(INFER_DIR, game, f"results/{args.task_name}")
        # get any one json from above path
        result_sample_json = [
            f
            for f in os.listdir(result_sample_path)
            if os.path.isfile(os.path.join(result_sample_path, f))
        ][0]
        # get the cutoff step from the json
        cutoff_step[game] = get_cutoff(
            os.path.join(result_sample_path, result_sample_json)
        )

    # write the cutoff step to json in EVAL_DIR
    with open(os.path.join(EVAL_DIR, f"cutoff_step_{args.model_name}.json"), "w") as f:
        json.dump(cutoff_step, f, indent=4, sort_keys=True)
