# this function serves to read off cutoff step from fjd's infered data
# "config": {
#     "model": "gpt-3.5-turbo",
#     "temperature": 0,
#     "system_message": "",
#     "load_path": [
#         "/share/data/ripl/fjd/gpt-games/chats/905/905.walkthrough_55.json",
#         "/share/data/ripl/fjd/gpt-games/chats/905/905.action_space.json",
#         "/share/data/ripl/fjd/gpt-games/chats/905/905.place_names.json"
#     ],
#     "save_path": "outputs/905/results/"
# },
# it's the last num from walkthrough json filename in the config field as above

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
    cutoff_step = {}

    # get game name available from infered result dir
    games = [
        f
        for f in os.listdir(INFER_DIR)
        if os.path.isdir(os.path.join(INFER_DIR, f)) and not f.startswith(".")
    ]
    print(len(games))

    for game in games:
        result_sample_path = os.path.join(INFER_DIR, game, "results/path_gen_llama")
        # get any one json from above path 
        result_sample_json = [
            f
            for f in os.listdir(result_sample_path)
            if os.path.isfile(os.path.join(result_sample_path, f))
        ][0]
        # get the cutoff step from the json
        cutoff_step[game] = get_cutoff(os.path.join(result_sample_path, result_sample_json))
    
    # write the cutoff step to json in EVAL_DIR
    with open(os.path.join(EVAL_DIR, "cutoff_step_llama.json"), "w") as f:
        json.dump(cutoff_step, f, indent=4, sort_keys=True)

