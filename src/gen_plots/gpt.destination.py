# generate dummy acc number for model A and model B, 53 entry each, use random number btw 0.3 and 1
import json
import math
import os

import matplotlib.pyplot as plt
import numpy as np
from colors import COLOR_MAP


def random_guess_rate(all2all, code2anno):
    """
    for stepnav, random guess correctness rate is 1/num_locations
    for pathgen, random guess correctness rate is (1/{num_actions + stop})^avg_path_len
    """
    total_steps = 0
    total_entries = float(len(all2all))
    for each in all2all:
        total_steps += int(each["step_count"])
    avg_entries = total_steps / total_entries

    total_locs = len(code2anno.keys())

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
random_scores = []

# get number of entry in each game folder
for game_name in game_names:
    all2all_path = f"./data/maps-release/{game_name}/{game_name}.all2all.json"
    code2anno_path = f"./data/maps-release/{game_name}/{game_name}.code2anno.json"
    all2all = json.load(open(all2all_path))
    code2anno = json.load(open(code2anno_path))
    random_rate = random_guess_rate(all2all, code2anno)
    # json load the file and count entry number
    random_scores.append(random_rate[0])  # destination finding is stepnav


model1_scores = np.random.uniform(0.3, 1, num_games)
model2_scores = np.random.uniform(0.3, 1, num_games)


# ============== following is the plotting part ==============

plt.figure(figsize=(4, 20))
plt.tight_layout()

# Calculate the width for each bar group
bar_width = 5
space_btw_bar = 1

# Set the positions of the bars on the x-axis
r1 = np.arange(len(game_names)) * 20
r2 = [x + (bar_width + space_btw_bar) for x in r1]
r3 = [x - (bar_width + space_btw_bar) for x in r1]

# Make the plot
plt.barh(
    r1,
    model1_scores,
    height=bar_width,
    label="GPT-3.5-turbo",
    color=COLOR_MAP["gpt3.5"],
)
plt.barh(r2, model2_scores, height=bar_width, label="GPT-4", color=COLOR_MAP["gpt4"])
plt.barh(
    r3, random_scores, height=bar_width, label="random guess", color=COLOR_MAP["random"]
)

# Set the y-axis labels as test names
whitespace = 0.02 * max(r1)
plt.ylim(-whitespace, max(r1) + 4 * whitespace)  # Adjust the y-axis limits as needed
plt.yticks(r1, game_names)

# Set the labels and title
plt.xlabel("accuracy of destination finding")

# Convert x-axis labels to percentage scores for specific ticks
plt.xlim(0, 1.1)
plt.xticks([0, 0.25, 0.5, 0.75, 1.0], ["0%", "25%", "50%", "75%", "100%"])

# Add dotted lines at x=0.5 and x=1
plt.axvline(0.25, color="gray", linestyle="dotted")
plt.axvline(0.5, color="gray", linestyle="dotted")
plt.axvline(0.75, color="gray", linestyle="dotted")
plt.axvline(1, color="gray", linestyle="dotted")

# Move the legend to the upper right corner
plt.legend(loc="upper right", ncol=1)

# Save the plot as a PNG file
png_path = "./evals/scoreboard_destination.png"
plt.savefig(png_path, bbox_inches='tight', dpi=300)

# Display the plot
plt.show()
