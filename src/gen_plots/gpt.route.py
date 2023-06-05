# generate dummy acc number for model A and model B, 53 entry each, use random number btw 0.3 and 1
import json
import math
import os

import matplotlib.pyplot as plt
import numpy as np
from colors import COLOR_MAP

GLOBAL_FONTSIZE = 13


def random_guess_rate(all2all, anno2code):
    """
    for stepnav, random guess correctness rate is 1/num_locations
    for pathgen, random guess correctness rate is (1/{num_actions + stop})^avg_path_len
    """
    total_steps = 0
    total_entries = float(len(all2all))
    for each in all2all:
        total_steps += int(each["step_count"])
    avg_entries = total_steps / total_entries

    total_locs = len(anno2code.keys())

    stepnav_random_guess_rate = 1.0 / total_locs
    pathgen_random_guess_rate = math.pow(1.0 / (total_locs + 1), avg_entries)
    return stepnav_random_guess_rate, pathgen_random_guess_rate


# get game names from ./data/maps-release, the folder names are the game names
game_names = os.listdir("./data/maps-release")
# sort by alphabetical order
game_names.sort(reverse=True)
num_games = len(game_names)
print(len(game_names))

# random scores
np.random.seed(25)
random_scores = {}

# get number of entry in each game folder
for game_name in game_names:
    all2all_path = f"./data/maps-release/{game_name}/{game_name}.all2all.json"
    anno2code_path = f"./data/maps-release/{game_name}/{game_name}.anno2code.json"
    all2all = json.load(open(all2all_path))
    anno2code = json.load(open(anno2code_path))
    random_desti, random_route = random_guess_rate(all2all, anno2code)
    # json load the file and count entry number
    random_scores[game_name] = random_route


# generate zero array
model1_scores = np.zeros(num_games)
model2_scores = np.zeros(num_games)

# update these to a dict like random_scores
model1_scores = {k: model1_scores[i] for i, k in enumerate(game_names)}
model2_scores = {k: model2_scores[i] for i, k in enumerate(game_names)}

# load real data from ./data/{model}
model1_real_path = "./src/gen_plots/data/gpt3.5/route.json"
model2_real_path = "./src/gen_plots/data/gpt4/route.json"
model1_real = json.load(open(model1_real_path))
model2_real = json.load(open(model2_real_path))
# "905": {
#     "desti_harsh": 1.0,
#     "desti_nice": 1.0,
#     "route_harsh": 1.0,
#     "route_nice": 1.0
# },
# replace fake data with real data, use nice version, skip if game name missed
for game_name in game_names:
    if game_name in model1_real:
        model1_scores[game_name] = model1_real[game_name]["nice"]
    if game_name in model2_real:
        model2_scores[game_name] = model2_real[game_name]["nice"]

# # skip games that are not in the real data by edit the game_names list
# game_names = [
#     each for each in game_names if each in model1_real and each in model2_real
# ]

# ============== following is the plotting part ==============

plt.figure(figsize=(4, 20))
plt.tight_layout()

# Calculate the width for each bar group
bar_width = 5
space_btw_bar = 1

# Set the positions of the bars on the x-axis
r2 = np.arange(len(game_names)) * 20
r1 = [x + (bar_width + space_btw_bar) for x in r2]
r3 = [x - (bar_width + space_btw_bar) for x in r2]

# Make the plot
plt.barh(
    r1,
    [random_scores[each] for each in game_names],
    height=bar_width,
    label="random guess",
    color=COLOR_MAP["random"],
)
plt.barh(
    r2,
    [model1_scores[each] for each in game_names],
    height=bar_width,
    label="GPT-3.5-turbo",
    color=COLOR_MAP["gpt3.5"],
)
plt.barh(
    r3,
    [model2_scores[each] for each in game_names],
    height=bar_width,
    label="GPT-4",
    color=COLOR_MAP["gpt4"],
)

# Set the y-axis labels as test names
whitespace = 0.02 * max(r1)
plt.ylim(-whitespace, max(r1) + 4 * whitespace)  # Adjust the y-axis limits as needed
plt.yticks(r1, game_names, fontsize=GLOBAL_FONTSIZE)

# Set the labels and title
plt.xlabel("accuracy of route finding", fontsize=GLOBAL_FONTSIZE)

# Convert x-axis labels to percentage scores for specific ticks
plt.xlim(0, 1.1)
plt.xticks(
    [0, 0.25, 0.5, 0.75, 1.0],
    ["0%", "25%", "50%", "75%", "100%"],
    fontsize=GLOBAL_FONTSIZE,
)

# Add dotted lines at x=0.5 and x=1
plt.axvline(0.25, color="gray", linestyle="dotted")
plt.axvline(0.5, color="gray", linestyle="dotted")
plt.axvline(0.75, color="gray", linestyle="dotted")
plt.axvline(1, color="gray", linestyle="dotted")

# Move the legend to the upper right corner
plt.legend(loc="upper right", ncol=1)

# Save the plot as a PNG file
png_path = "./evals/scoreboard_route.png"
plt.savefig(png_path, bbox_inches="tight", dpi=300)

# Display the plot
plt.show()
