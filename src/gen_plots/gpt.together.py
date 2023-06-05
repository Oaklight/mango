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

# Generate dummy random scores for each model and task
np.random.seed(25)
random_scores_DF = {}
random_scores_RF = {}

# get number of entry in each game folder
for game_name in game_names:
    all2all_path = f"./data/maps-release/{game_name}/{game_name}.all2all.json"
    anno2code_path = f"./data/maps-release/{game_name}/{game_name}.anno2code.json"
    all2all = json.load(open(all2all_path))
    anno2code = json.load(open(anno2code_path))
    random_desti, random_route = random_guess_rate(all2all, anno2code)
    # json load the file and count entry number
    random_scores_DF[game_name] = random_desti
    random_scores_RF[game_name] = random_route


model1_scores_DF = np.random.uniform(0.3, 1, num_games)
model2_scores_DF = np.random.uniform(0.3, 1, num_games)
model1_scores_RF = np.random.uniform(0.3, 1, num_games)
model2_scores_RF = np.random.uniform(0.3, 1, num_games)
model1_scores_DF = {k: model1_scores_DF[i] for i, k in enumerate(game_names)}
model2_scores_DF = {k: model2_scores_DF[i] for i, k in enumerate(game_names)}
model1_scores_RF = {k: model1_scores_RF[i] for i, k in enumerate(game_names)}
model2_scores_RF = {k: model2_scores_RF[i] for i, k in enumerate(game_names)}

# load real data from ./data/{model}
model1_real_path_route = "./src/gen_plots/data/gpt3.5/route.json"
model2_real_path_route = "./src/gen_plots/data/gpt4/route.json"
model1_real_path_desti = "./src/gen_plots/data/gpt3.5/desti.json"
model2_real_path_desti = "./src/gen_plots/data/gpt4/desti.json"
model1_real_route = json.load(open(model1_real_path_route))
model2_real_route = json.load(open(model2_real_path_route))
model1_real_desti = json.load(open(model1_real_path_desti))
model2_real_desti = json.load(open(model2_real_path_desti))
# "905": {
#     "desti_harsh": 1.0,
#     "desti_nice": 1.0,
#     "route_harsh": 1.0,
#     "route_nice": 1.0
# },
# replace fake data with real data, use nice version, skip if game name missed
for game_name in game_names:
    # route
    if game_name in model1_real_route:
        model1_scores_RF[game_name] = model1_real_route[game_name]["nice"]
    if game_name in model2_real_route:
        model2_scores_RF[game_name] = model2_real_route[game_name]["nice"]
    # desti
    if game_name in model1_real_desti:
        model1_scores_DF[game_name] = model1_real_desti[game_name]["nice"]
    if game_name in model2_real_desti:
        model2_scores_DF[game_name] = model2_real_desti[game_name]["nice"]

# ============== following is the plotting part ==============

# Set the figure size and create subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 20), sharey=True)
plt.tight_layout()

# Calculate the width for each bar group
bar_width = 6
space_btw_bar = 1

# Set the positions of the bars on the x-axis
r2 = np.arange(len(game_names)) * 30
r1 = [x + (bar_width + space_btw_bar) for x in r2]
r3 = [x - (bar_width + space_btw_bar) for x in r2]

# Plot the scores for DF - Model 1, Model 2, and Random
ax1.barh(
    r1,
    [random_scores_DF[each] for each in game_names],
    height=bar_width,
    label="random guess",
    color=COLOR_MAP["random"],
)
ax1.barh(
    r2,
    [model1_scores_DF[each] for each in game_names],
    height=bar_width,
    label="GPT-3.5-turbo",
    color=COLOR_MAP["gpt3.5"],
)
ax1.barh(
    r3,
    [model2_scores_DF[each] for each in game_names],
    height=bar_width,
    label="GPT-4",
    color=COLOR_MAP["gpt4"],
)

# Plot the scores for RF - Model 1, Model 2, and Random
ax2.barh(
    r1,
    [random_scores_RF[each] for each in game_names],
    height=bar_width,
    label="random guess",
    color=COLOR_MAP["random"],
)
ax2.barh(
    r2,
    [model1_scores_RF[each] for each in game_names],
    height=bar_width,
    label="GPT-3.5-turbo",
    color=COLOR_MAP["gpt3.5"],
)
ax2.barh(
    r3,
    [model2_scores_RF[each] for each in game_names],
    height=bar_width,
    label="GPT-4",
    color=COLOR_MAP["gpt4"],
)

# Set the y-axis labels as test names
whitespace = 0.02 * max(r2)
ax1.set_ylim(
    -whitespace, max(r2) + 2.5 * whitespace
)  # Adjust the y-axis limits as needed
ax1.set_yticks(r2, game_names, fontsize=GLOBAL_FONTSIZE, ha="left")
ax1.yaxis.tick_right()

# Set the x-axis labels
ax1.set_xlabel("accuracy of destination finding", fontsize=GLOBAL_FONTSIZE)
ax2.set_xlabel("accuracy of route finding", fontsize=GLOBAL_FONTSIZE)

# Set the x-axis limits
ax1.set_xlim(1.1, 0)  # Set the x-axis range for DF
ax2.set_xlim(0, 1.1)  # Set the x-axis range for RF
ax1.set_xticks(
    [0, 0.25, 0.5, 0.75, 1.0],
    ["0%", "25%", "50%", "75%", "100%"],
    fontsize=GLOBAL_FONTSIZE,
)
ax2.set_xticks(
    [0, 0.25, 0.5, 0.75, 1.0],
    ["0%", "25%", "50%", "75%", "100%"],
    fontsize=GLOBAL_FONTSIZE,
)

# Add dotted lines at x=0.5 and x=1
ax1.axvline(0.25, color="gray", linestyle="dotted")
ax1.axvline(0.5, color="gray", linestyle="dotted")
ax1.axvline(0.75, color="gray", linestyle="dotted")
ax1.axvline(1, color="gray", linestyle="dotted")
ax2.axvline(0.25, color="gray", linestyle="dotted")
ax2.axvline(0.5, color="gray", linestyle="dotted")
ax2.axvline(0.75, color="gray", linestyle="dotted")
ax2.axvline(1, color="gray", linestyle="dotted")

# # Set the title for each subplot
# ax1.set_title("DF Scores")
# ax2.set_title("RF Scores")

# Move the legend to the upper right corner with a row layout
# Create a single legend for both subplots in the upper center position
handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
handles = handles1 + handles2
labels = labels1 + labels2

unique_labels = []
unique_handles = []
for handle, label in zip(handles, labels):
    if label not in unique_labels:
        unique_labels.append(label)
        unique_handles.append(handle)

fig.legend(
    unique_handles,
    unique_labels,
    loc="upper center",
    ncol=3,
    fontsize="large",
    bbox_to_anchor=(0.5, 0.99),
)

# Add extra space on the left and right sides of the plot
plt.subplots_adjust(wspace=0.5)  # Adjust the value as needed

# Save the plot as a PNG file
png_path = "./evals/scoreboard_together.png"
plt.savefig(png_path, bbox_inches="tight", dpi=300)

# Display the plot
plt.show()
