# this function serves to compute the linear regression of the trend line in each game acc vs dist plot

import json
import os
import sys

import numpy as np
from matplotlib import pyplot as plt
from scipy import stats

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from gen_evals.utils import __count_helper_trend

EVAL_DIR = "./evals"


def plot_acc_vs_term_dist(save_path, length_acc):
    length_acc = sorted(length_acc.items(), key=lambda x: x[0])
    micro_length = [each[0] for each in length_acc]
    micro_acc = [
        each[1]["good"] / (each[1]["good"] + each[1]["bad"]) for each in length_acc
    ]

    # Perform linear regression for micro data
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        micro_length, micro_acc
    )
    conf_int = stats.t.interval(0.95, len(micro_length) - 2, loc=slope, scale=std_err)

    # Generate fitted line
    micro_line = np.poly1d([slope, intercept])

    plt.figure(figsize=(10, 10))
    plt.plot(micro_length, micro_acc)
    plt.plot(micro_length, micro_line(micro_length), "--r", label="Fitted line")
    plt.xlabel("dist(src, dst)")
    plt.ylabel("accuracy")

    # Add slope and confidence interval to the plot
    plt.text(0.7, 0.9, f"Slope: {slope:.2f}", transform=plt.gca().transAxes)
    plt.text(
        0.7,
        0.85,
        f"Confidence Interval: [{conf_int[0]:.2f}, {conf_int[1]:.2f}]",
        transform=plt.gca().transAxes,
    )

    plt.savefig(save_path)
    plt.close()
    return slope, conf_int


def plot_acc_vs_route_length(save_path, macro_length_acc):
    macro_length_acc = sorted(macro_length_acc.items(), key=lambda x: x[0])
    macro_length = [each[0] for each in macro_length_acc]
    macro_acc = [
        each[1]["good"] / (each[1]["good"] + each[1]["bad"])
        for each in macro_length_acc
    ]

    # Perform linear regression for macro data
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        macro_length, macro_acc
    )
    conf_int = stats.t.interval(0.95, len(macro_length) - 2, loc=slope, scale=std_err)

    # Generate fitted line
    macro_line = np.poly1d([slope, intercept])

    plt.figure(figsize=(10, 10))
    plt.plot(macro_length, macro_acc)
    plt.plot(macro_length, macro_line(macro_length), "--r", label="Fitted Line")
    plt.xlabel("requested route length")
    plt.ylabel("accuracy")

    # Add slope and confidence interval to the plot
    plt.text(0.7, 0.9, f"Slope: {slope:.2f}", transform=plt.gca().transAxes)
    plt.text(
        0.7,
        0.85,
        f"Confidence Interval: [{conf_int[0]:.2f}, {conf_int[1]:.2f}]",
        transform=plt.gca().transAxes,
    )

    plt.savefig(save_path)
    plt.close()
    return slope, conf_int


def plot_acc_vs_sth_for_task(current_collection, save_path, task="desti"):
    assert task in ["desti", "route"], "task must be one of [desti, route]"

    slope, conf_int = None, None
    if task == "route":  # only care about macro level finding
        macro_acc_vs_term_dist = __count_helper_trend(
            current_collection, level="macro", field="dist_shortest"
        )
        # plot acc vs length
        slope, conf_int = plot_acc_vs_term_dist(save_path, macro_acc_vs_term_dist)
        print(f"[route] acc vs term dist plotted: [{save_path}]")

    elif task == "desti":  # only care about micro level finding
        micro_acc_vs_route_length = __count_helper_trend(
            current_collection, level="micro", field="route_length"
        )
        slope, conf_int = plot_acc_vs_route_length(save_path, micro_acc_vs_route_length)
        print(f"[desti] acc vs route length plotted: [{save_path}]")

    # if slope, conf_int is nan, then return None, otherwise return slope, conf_int
    slope = slope if not np.isnan(slope) else None
    conf_int = conf_int if not np.isnan(conf_int[0]) else None
    return slope, conf_int


# get model names in the eval dir
model_names = [
    each for each in os.listdir(EVAL_DIR) if os.path.isdir(os.path.join(EVAL_DIR, each))
]

# get games under each model's eval dir
for each_model in model_names:
    each_model_dir = os.path.join(EVAL_DIR, each_model)
    # there should be "desti" and "route" folders under each model dir, within which are games folders
    # there should be "destination.harsh.json" and "destination.nice.json" in "desti/{game}" dir
    # there should be "route.harsh.json" and "route.nice.json" in "route/{game}" dir

    # process desti
    print("======== processing DESTINATION finding plots ========")
    desti_dir = os.path.join(each_model_dir, "desti")
    desti_games = [
        each
        for each in os.listdir(desti_dir)
        if os.path.isdir(os.path.join(desti_dir, each))
    ]

    slope_dict_harsh = {}
    conf_int_dict_harsh = {}
    slope_dict_nice = {}
    conf_int_dict_nice = {}

    for each_game in desti_games:
        each_game_dir = os.path.join(desti_dir, each_game)
        # there should be "destination.harsh.json" and "destination.nice.json" in "desti/{game}" dir
        # destination finding should care about path level (micro / instance level)

        # "collection_micro": [...]
        # "correct_num_micro": 122,
        # "total_num_micro": 181,
        # "accuracy_micro": 0.6740331491712708,

        # ============ HARSH ============
        harsh_json = os.path.join(each_game_dir, "destination.harsh.json")
        harsh_results = list(json.load(open(harsh_json, "r")).values())[0]
        harsh_collection = harsh_results["collection_micro"]
        # [desti finding] plot acc vs requested route length
        save_path = os.path.join(
            each_game_dir, "desti_finding_acc_vs_route_length.harsh.png"
        )
        slope, conf_int = plot_acc_vs_sth_for_task(
            harsh_collection, save_path, task="desti"
        )
        # add to dict
        slope_dict_harsh[each_game] = slope
        conf_int_dict_harsh[each_game] = conf_int

        # ============ NICE ============
        nice_json = os.path.join(each_game_dir, "destination.nice.json")
        nice_results = list(json.load(open(nice_json, "r")).values())[0]
        nice_collection = nice_results["collection_micro"]
        # [desti finding] plot acc vs requested route length
        save_path = os.path.join(
            each_game_dir, "desti_finding_acc_vs_route_length.nice.png"
        )
        slope, conf_int = plot_acc_vs_sth_for_task(
            nice_collection, save_path, task="desti"
        )
        # add to dict
        slope_dict_nice[each_game] = slope
        conf_int_dict_nice[each_game] = conf_int

    # ======== save to json ========
    # merge slope and conf_int into one dict for harsh
    slope_conf_int_dict_harsh = {
        each_game: {
            "slope": slope_dict_harsh[each_game],
            "conf_int": conf_int_dict_harsh[each_game],
        }
        for each_game in slope_dict_harsh
    }
    # merge slope and conf_int into one dict for nice
    slope_conf_int_dict_nice = {
        each_game: {
            "slope": slope_dict_nice[each_game],
            "conf_int": conf_int_dict_nice[each_game],
        }
        for each_game in slope_dict_nice
    }
    # save to json
    json.dump(
        slope_conf_int_dict_harsh,
        open(os.path.join(desti_dir, "desti_finding_error_bar_reg_harsh.json"), "w"),
        indent=4,
        sort_keys=True,
    )
    json.dump(
        slope_conf_int_dict_nice,
        open(os.path.join(desti_dir, "desti_finding_error_bar_reg_nice.json"), "w"),
        indent=4,
        sort_keys=True,
    )

    # process route
    print("======== processing ROUTE finding plots ========")
    route_dir = os.path.join(each_model_dir, "route")
    route_games = [
        each
        for each in os.listdir(route_dir)
        if os.path.isdir(os.path.join(route_dir, each))
    ]

    slope_dict_harsh = {}
    conf_int_dict_harsh = {}
    slope_dict_nice = {}
    conf_int_dict_nice = {}

    for each_game in route_games:
        each_game_dir = os.path.join(route_dir, each_game)
        # there should be "route.harsh.json" and "route.nice.json" in "route/{game}" dir
        # route finding should care about path level (macro / game level)

        # "collection_macro": [...]
        # "correct_num_macro": 122,
        # "total_num_macro": 181,
        # "accuracy_macro": 0.6740331491712708,

        # ============ HARSH ============
        harsh_json = os.path.join(each_game_dir, "route.harsh.json")
        harsh_results = list(json.load(open(harsh_json, "r")).values())[0]
        harsh_collection = harsh_results["collection_macro"]
        # [route finding] plot acc vs requested route length
        save_path = os.path.join(
            each_game_dir, "route_finding_acc_vs_term_dist.harsh.png"
        )
        slope, conf_int = plot_acc_vs_sth_for_task(
            harsh_collection, save_path, task="route"
        )
        # add to dict
        slope_dict_harsh[each_game] = slope
        conf_int_dict_harsh[each_game] = conf_int

        # ============ NICE ============
        nice_json = os.path.join(each_game_dir, "route.nice.json")
        nice_results = list(json.load(open(nice_json, "r")).values())[0]
        nice_collection = nice_results["collection_macro"]
        # [route finding] plot acc vs requested route length
        save_path = os.path.join(
            each_game_dir, "route_finding_acc_vs_term_dist.nice.png"
        )
        slope, conf_int = plot_acc_vs_sth_for_task(
            nice_collection, save_path, task="route"
        )
        # add to dict
        slope_dict_nice[each_game] = slope
        conf_int_dict_nice[each_game] = conf_int

    # ======== save to json ========
    # merge slope and conf_int into one dict for harsh
    slope_conf_int_dict_harsh = {
        each_game: {
            "slope": slope_dict_harsh[each_game],
            "conf_int": conf_int_dict_harsh[each_game],
        }
        for each_game in slope_dict_harsh
    }
    # merge slope and conf_int into one dict for nice
    slope_conf_int_dict_nice = {
        each_game: {
            "slope": slope_dict_nice[each_game],
            "conf_int": conf_int_dict_nice[each_game],
        }
        for each_game in slope_dict_nice
    }
    # save to json
    json.dump(
        slope_conf_int_dict_harsh,
        open(os.path.join(route_dir, "route_finding_error_bar_reg_harsh.json"), "w"),
        indent=4,
        sort_keys=True,
    )
    json.dump(
        slope_conf_int_dict_nice,
        open(os.path.join(route_dir, "route_finding_error_bar_reg_nice.json"), "w"),
        indent=4,
        sort_keys=True,
    )
