# for each game, load the map

import json
import os
import sys

import pandas as pd

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from gen_paths.gamegraph import build_graph_from_file_with_reverse

MAP_DIR = "./data/maps"
RELEASE_MAP_DIR = "./data/maps-release"
CUTOFF_FILE = "evals/cutoff_step_fjd.json"

# load cutoff steps
with open(CUTOFF_FILE, "r") as f:
    cutoff_steps = json.load(f)

stats = {}

games = sorted(os.listdir(RELEASE_MAP_DIR))

for game in games:
    print(f"================== processing [{game}] =================")
    game_cutoff = cutoff_steps[game]

    game_dir = os.path.join(MAP_DIR, game)  # use dev maps for more util files
    cutoff_map_json = os.path.join(game_dir, f"{game}.node_step.json")
    all2all_json = os.path.join(game_dir, f"{game}.all2all.json")

    map_reversed_file = os.path.join(game_dir, f"{game}.map.reversed")
    map_human_file = os.path.join(game_dir, f"{game}.map.human")

    # load files
    with open(cutoff_map_json, "r") as f:
        node_cutoff_map = json.load(f)
    with open(all2all_json, "r") as f:
        all2all = json.load(f)

    g = build_graph_from_file_with_reverse(
        map_human_file, map_reversed_file, verbose=False
    )

    G_NODE_NUM_BEFORE_CUTOFF = len(g.nodes)
    G_EDGE_NUM_BEFORE_CUTOFF = len(g.edges)

    drop_nodes = set()
    for node in g.nodes:
        # drop the node in g and g.forward and g.backward when the node is not in the cutoff map
        assert node in node_cutoff_map, f"{node} not in cutoff map SOMETHING IS WRONG!"

        if node_cutoff_map[node] > game_cutoff:
            drop_nodes.add(node)

    for i, each in enumerate(drop_nodes):
        assert each in g.nodes, f"{each} not in g.nodes SOMETHING IS WRONG!"

        print(f"dropping node {i+1}/{len(drop_nodes)}: {each}")
        g.remove_node(each)

    G_NODE_NUM_AFTER_CUTOFF = len(g.nodes)
    G_EDGE_NUM_AFTER_CUTOFF = len(g.edges)

    all2all_after_cutoff = []
    for each in all2all:
        # "step_count": 3,
        # "path_min_cutoff": 17,
        # "all_steps_seen_in_forward": true
        if each["path_min_cutoff"] > game_cutoff:
            continue
        all2all_after_cutoff.append(each)

    ALL2ALL_BEFORE_CUTOFF = len(all2all)
    ALL2ALL_AFTER_CUTOFF = len(all2all_after_cutoff)

    ALL_STEPS_SEEN_IN_FORWARD_BEFORE_CUTOFF = ALL2ALL_BEFORE_CUTOFF
    for each in all2all:
        if each["all_steps_seen_in_forward"] == False:
            ALL_STEPS_SEEN_IN_FORWARD_BEFORE_CUTOFF -= 1

    ALL_STEPS_SEEN_IN_FORWARD_AFTER_CUTOFF = ALL2ALL_AFTER_CUTOFF
    for each in all2all_after_cutoff:
        if each["all_steps_seen_in_forward"] == False:
            ALL_STEPS_SEEN_IN_FORWARD_AFTER_CUTOFF -= 1

    stats[game] = {
        "before_cutoff": {
            "node_num": G_NODE_NUM_BEFORE_CUTOFF,
            "edge_num": G_EDGE_NUM_BEFORE_CUTOFF,
            "all2all": ALL2ALL_BEFORE_CUTOFF,
            "all_steps_seen_in_forward": ALL_STEPS_SEEN_IN_FORWARD_BEFORE_CUTOFF,
        },
        "after_cutoff": {
            "node_num": G_NODE_NUM_AFTER_CUTOFF,
            "edge_num": G_EDGE_NUM_AFTER_CUTOFF,
            "all2all": ALL2ALL_AFTER_CUTOFF,
            "all_steps_seen_in_forward": ALL_STEPS_SEEN_IN_FORWARD_AFTER_CUTOFF,
        },
    }

# dump stats
with open("evals/map_stats.json", "w") as f:
    json.dump(stats, f, indent=4, sort_keys=True)


# load gpt4 nice route scores
gpt4_nice_route_json = "./temp_data/gpt/gpt4/route.json"
with open(gpt4_nice_route_json, "r") as f:
    gpt4_nice_route_scores = json.load(f)


more_than_50 = []
acc_more_than_50 = []
less_than_50 = []
acc_less_than_50 = []
for game in games:
    print("==========================")
    nice_score = float(gpt4_nice_route_scores[game]["nice"])
    print(f"{game}: {nice_score}")
    if nice_score >= 0.5:
        print(f"more than 50: {game}")
        more_than_50.append(game)
        acc_more_than_50.append(nice_score)
    else:
        print(f"less than 50: {game}")
        less_than_50.append(game)
        acc_less_than_50.append(nice_score)

avg_acc_more_than_50 = (
    sum(acc_more_than_50) / len(acc_more_than_50) if len(acc_more_than_50) > 0 else 0
)
avg_acc_less_than_50 = (
    sum(acc_less_than_50) / len(acc_less_than_50) if len(acc_less_than_50) > 0 else 0
)

print(f"these games have nice score more than 50: {more_than_50}")
print(f"these games have nice score less than 50: {less_than_50}")

# create pandas chart for more_than_50 games
more_than_50_stats = {}
for game in more_than_50:
    more_than_50_stats[game] = stats[game]["after_cutoff"]
    more_than_50_stats[game]["ratio_of_all_steps_seen_to_all2all"] = (
        more_than_50_stats[game]["all_steps_seen_in_forward"]
        / more_than_50_stats[game]["all2all"]
    )
    more_than_50_stats[game]["nice_score"] = gpt4_nice_route_scores[game]["nice"]
    more_than_50_stats[game]["avg_acc_more_than_50"] = avg_acc_more_than_50

more_than_50_df = pd.DataFrame.from_dict(more_than_50_stats, orient="index")
# save to csv
more_than_50_df.to_csv("evals/map_stats_more_than_50.csv")

# do the same for under 50
less_than_50_stats = {}
for game in less_than_50:
    less_than_50_stats[game] = stats[game]["after_cutoff"]
    less_than_50_stats[game]["ratio_of_all_steps_seen_to_all2all"] = (
        less_than_50_stats[game]["all_steps_seen_in_forward"]
        / less_than_50_stats[game]["all2all"]
    )
    less_than_50_stats[game]["nice_score"] = gpt4_nice_route_scores[game]["nice"]
    less_than_50_stats[game]["avg_acc_less_than_50"] = avg_acc_less_than_50

less_than_50_df = pd.DataFrame.from_dict(less_than_50_stats, orient="index")
# save to csv
less_than_50_df.to_csv("evals/map_stats_less_than_50.csv")
