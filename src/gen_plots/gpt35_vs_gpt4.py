# this function serves to create nice vs harsh accuracy plots for destination and route tasks on gpt family models

import json

import matplotlib.pyplot as plt
import numpy as np

TEMP_DIR = "./src/gen_plots/data"
EVAL_DIR = "./evals"
GLOBAL_FONTSIZE = 13
# read in data from TEMP_DIR for each model

# model1: gpt3.5, model2: gpt4
model1_nice_scores = []
model1_harsh_scores = []
model2_nice_scores = []
model2_harsh_scores = []

# read in data from TEMP_DIR for each model
model1_real_path_route = TEMP_DIR + "/gpt3.5/route.json"
model2_real_path_route = TEMP_DIR + "/gpt4/route.json"
model1_real_path_desti = TEMP_DIR + "/gpt3.5/desti.json"
model2_real_path_desti = TEMP_DIR + "/gpt4/desti.json"

model1_real_route = json.load(open(model1_real_path_route))
model2_real_route = json.load(open(model2_real_path_route))
model1_real_desti = json.load(open(model1_real_path_desti))
model2_real_desti = json.load(open(model2_real_path_desti))

# get game names, anything other than "avg_harsh" and "avg_nice"
game_names = [
    key for key in model1_real_route.keys() if key not in ["avg_harsh", "avg_nice"]
]

# get nice and harsh scores for each game
for game_name in game_names:
    model1_nice_scores.append(model1_real_route[game_name]["nice"])
    model1_harsh_scores.append(model1_real_route[game_name]["harsh"])
    model2_nice_scores.append(model2_real_route[game_name]["nice"])
    model2_harsh_scores.append(model2_real_route[game_name]["harsh"])


# plot gpt4 vs gpt3.5 avg acc for each task, gpt3.5 as x axis, gpt4 as y axis, and a trend line y=x, add game name to each point
def plot_vs(savepath, font_size, model1_nice_scores, model2_nice_scores, game_names):
    plt.figure(figsize=(10, 10))
    plt.tight_layout()
    plt.scatter(model1_nice_scores, model2_nice_scores, s=200, alpha=0.5)
    plt.plot([0, 1], [0, 1], color="lightcoral", linestyle="--", alpha=0.8)

    # add text to each point
    for i, game_name in enumerate(game_names):
        plt.annotate(
            game_name,
            (model1_nice_scores[i], model2_nice_scores[i]),
            xytext=(8, 8),
            textcoords="offset points",
            ha="left",
            va="top",
            fontsize=10,
        )
    plt.xlabel("gpt3.5", fontsize=font_size)
    plt.ylabel("gpt4", fontsize=font_size)
    plt.xticks(fontsize=font_size)
    plt.savefig(savepath, dpi=300, bbox_inches="tight")
    plt.show()


# nice version
plot_vs(
    EVAL_DIR + "/gpt35_vs_gpt4_nice.png",
    GLOBAL_FONTSIZE,
    model1_nice_scores,
    model2_nice_scores,
    game_names,
)
# harsh version
plot_vs(
    EVAL_DIR + "/gpt35_vs_gpt4_harsh.png",
    GLOBAL_FONTSIZE,
    model1_harsh_scores,
    model2_harsh_scores,
    game_names,
)
