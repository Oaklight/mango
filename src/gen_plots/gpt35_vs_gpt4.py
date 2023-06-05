# this function serves to create nice vs harsh accuracy plots for destination and route tasks on gpt family models

import json

import matplotlib.pyplot as plt
import numpy as np

TEMP_DIR = "./src/gen_plots/data"
EVAL_DIR = "./evals"
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

# nice version
# plot gpt4 vs gpt3.5 avg acc for each task, gpt3.5 as x axis, gpt4 as y axis, and a trend line y=x
plt.figure(figsize=(10, 10))
plt.scatter(model1_nice_scores, model2_nice_scores)
plt.plot([0, 1], [0, 1], color="red")
plt.xlabel("gpt3.5")
plt.ylabel("gpt4")
plt.title("nice accuracy")
plt.savefig(EVAL_DIR + "/gpt35_vs_gpt4_nice.png")
plt.show()
