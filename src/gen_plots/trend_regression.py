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
GLOBAL_FONTSIZE = 11


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
    plt.plot(micro_length, micro_acc, color="steelblue", label="Accuracy")
    plt.plot(
        micro_length,
        micro_line(micro_length),
        linestyle="dashed",
        label="Fitted line",
        color="lightcoral",
    )
    plt.xlabel("dist(src, dst)", fontsize=GLOBAL_FONTSIZE)
    plt.ylabel("accuracy", fontsize=GLOBAL_FONTSIZE)

    # Add slope and confidence interval to the plot
    plt.text(
        0.7,
        0.9,
        f"Slope: {slope:.2f}",
        transform=plt.gca().transAxes,
        fontsize=GLOBAL_FONTSIZE,
    )
    plt.text(
        0.7,
        0.85,
        f"Confidence Interval: [{conf_int[0]:.2f}, {conf_int[1]:.2f}]",
        transform=plt.gca().transAxes,
        fontsize=GLOBAL_FONTSIZE,
    )

    plt.savefig(save_path, dpi=300, bbox_inches="tight")
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
    plt.plot(macro_length, macro_acc, color="steelblue", label="Accuracy")
    plt.plot(
        macro_length,
        macro_line(macro_length),
        linestyle="dashed",
        label="Fitted Line",
        color="lightcoral",
    )
    plt.xlabel("requested route length", fontsize=GLOBAL_FONTSIZE)
    plt.ylabel("accuracy", fontsize=GLOBAL_FONTSIZE)

    # Add slope and confidence interval to the plot
    plt.text(
        0.7,
        0.9,
        f"Slope: {slope:.2f}",
        transform=plt.gca().transAxes,
        fontsize=GLOBAL_FONTSIZE,
    )
    plt.text(
        0.7,
        0.85,
        f"Confidence Interval: [{conf_int[0]:.2f}, {conf_int[1]:.2f}]",
        transform=plt.gca().transAxes,
        fontsize=GLOBAL_FONTSIZE,
    )

    plt.savefig(save_path, dpi=300, bbox_inches="tight")
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
def regress_plot_individual_desti(plot_acc_vs_sth_for_task, each_model_dir):
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


def regress_plot_individual_route(plot_acc_vs_sth_for_task, each_model_dir):
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


def plot_slopes_with_error_bars(slope_data, save_path):
    test_names = []
    slopes = []
    conf_intervals = []
    for test in slope_data:
        if (
            slope_data[test]["slope"] is not None
            and slope_data[test]["conf_int"] is not None
        ):
            test_names.append(test)
            slopes.append(slope_data[test]["slope"])
            conf_intervals.append(slope_data[test]["conf_int"])
    # check if conf_intervals is a list of list of size 2
    assert all(
        [len(each) == 2 for each in conf_intervals]
    ), "conf_intervals should be a list of list of size 2"

    # Convert confidence intervals to error bars
    errors = np.abs(np.array(conf_intervals).T - np.array(slopes))

    # Plot the slopes with error bars
    plt.figure(figsize=(10, 6))
    # error bar plot
    plt.errorbar(
        test_names,
        slopes,
        yerr=errors,
        fmt="o",
        capsize=5,
        alpha=0.5,
        color="steelblue",
    )
    # # scattered plot
    # plt.scatter( # plot scattered points
    #     test_names,
    #     slopes,
    #     marker="o",
    #     color="steelblue",
    #     alpha=0.5,
    #     label="Slope",
    # )
    plt.ylabel("Slope", fontsize=GLOBAL_FONTSIZE)
    plt.xticks(rotation=30, ha="right", fontsize=GLOBAL_FONTSIZE)
    plt.yticks(fontsize=GLOBAL_FONTSIZE)
    # plt.subplots_adjust(bottom=0.2)
    # add horizontal dashed line at y=0, lightcoral
    plt.axhline(y=0, color="lightcoral", linestyle="dashed")

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    # plt.show()


def regress_plot_all_game(each_model_dir, task):
    assert task in ["desti", "route"], "task should be either desti or route"

    task_path = os.path.join(each_model_dir, task)

    harsh_slope_conf_int_dict = json.load(
        open(os.path.join(task_path, f"{task}_finding_error_bar_reg_harsh.json"), "r")
    )
    save_path = os.path.join(task_path, f"{task}_finding_error_bar_reg_harsh.png")
    plot_slopes_with_error_bars(harsh_slope_conf_int_dict, save_path)

    nice_slope_conf_int_dict = json.load(
        open(os.path.join(task_path, f"{task}_finding_error_bar_reg_nice.json"), "r")
    )
    save_path = os.path.join(task_path, f"{task}_finding_error_bar_reg_nice.png")
    plot_slopes_with_error_bars(nice_slope_conf_int_dict, save_path)


if __name__ == "__main__":
    for each_model in model_names:
        each_model_dir = os.path.join(EVAL_DIR, each_model)
        # there should be "desti" and "route" folders under each model dir, within which are games folders
        # there should be "destination.harsh.json" and "destination.nice.json" in "desti/{game}" dir
        # there should be "route.harsh.json" and "route.nice.json" in "route/{game}" dir

        # process desti
        regress_plot_individual_desti(plot_acc_vs_sth_for_task, each_model_dir)

        # # process route
        regress_plot_individual_route(plot_acc_vs_sth_for_task, each_model_dir)

        # process desti regression error bar for all games
        regress_plot_all_game(each_model_dir, "desti")
        # process route regression error bar for all games
        regress_plot_all_game(each_model_dir, "route")
