import os
import matplotlib.pyplot as plt
import numpy as np
from colors import COLOR_MAP
import pandas as pd

PLOT_DIR = "./plots"
EVAL_GPT = "./evals"
EVAL_LLAMA = "./evals_llama"
EVAL_RWKV = "./evals_rwkv"

# Define the global fontsize
GLOBAL_FONTSIZE = 14


def read_real_data(model_name, test_type):
    """
    Read the real data from the file
    """
    assert test_type in ["desti_nice", "desti_harsh", "route_nice", "route_harsh"]

    print(f"model_name: {model_name}, test_type: {test_type}")

    if "gpt" in model_name:
        eval_dir = EVAL_GPT
    elif "llama" in model_name:
        eval_dir = EVAL_LLAMA
    elif "rwkv" in model_name:
        eval_dir = EVAL_RWKV

    # Define the path
    # path = f"{eval_dir}/avg_acc.csv"
    # # Read the data
    # # data = pd.read_csv(path) if path exist otherwise return None
    # if os.path.exists(path):
    #     data = pd.read_csv(path, index_col=0)
    # else:
    #     data = None
    # if eval_dir exists, then read the data, otherwise return None
    if os.path.exists(eval_dir):
        path = f"{eval_dir}/avg_acc.csv"
        data = pd.read_csv(path, index_col=0)
        print(f"read data from {path}")
    else:
        data = None
        print(f"no data found at {eval_dir}")

    # test data is at [model_name, test_type]
    if data is None:
        rst = 0
    else:
        rst = data.loc[model_name, test_type]
        print(f"rst: {rst}")
    return rst


# Dummy data for model names
model_names = {
    "model1": "llama_anno",
    "model2": "llama",
    "model3": "rwkv_anno",
    "model4": "rwkv",
    "model5": "gpt3.5",
    "model6": "gpt4",
}

# Define the score dictionaries
avg_acc_route_nice = {
    "model1": 0.67,
    "model2": 0.67,
    "model3": 0.67,
    "model4": 0.67,
    "model5": 0.67,
    "model6": 0.67,
}

avg_acc_route_harsh = {
    "model1": 0.67,
    "model2": 0.67,
    "model3": 0.67,
    "model4": 0.67,
    "model5": 0.67,
    "model6": 0.67,
}

avg_acc_desti_nice = {
    "model1": 0.67,
    "model2": 0.67,
    "model3": 0.67,
    "model4": 0.67,
    "model5": 0.67,
    "model6": 0.67,
}

avg_acc_desti_harsh = {
    "model1": 0.67,
    "model2": 0.67,
    "model3": 0.67,
    "model4": 0.67,
    "model5": 0.67,
    "model6": 0.67,
}

# all_scores = [avg_acc_desti_nice, avg_acc_desti_harsh, avg_acc_route_nice, avg_acc_route_harsh]
all_scores = {
    "avg_acc_desti_nice": avg_acc_desti_nice,
    "avg_acc_desti_harsh": avg_acc_desti_harsh,
    "avg_acc_route_nice": avg_acc_route_nice,
    "avg_acc_route_harsh": avg_acc_route_harsh,
}

# load real data into all_scores
for test_type in ["desti_nice", "desti_harsh", "route_nice", "route_harsh"]:
    for model_key, model_name in model_names.items():
        all_scores[f"avg_acc_{test_type}"][model_key] = read_real_data(
            model_name, test_type
        )

print(f"all_scores: {all_scores}")

# Set the y range
y_range = (0, 1)

# Please adapt this above commented code to 4 separate plot, no subplot:
# 1. avg_acc_route_nice
# 2. avg_acc_route_harsh
# 3. avg_acc_desti_nice
# 4. avg_acc_desti_harsh

# Create the bar plot
for name, each in all_scores.items():
    fig = plt.figure(figsize=(10, 10))
    plt.tight_layout()

    colors = [COLOR_MAP[model_names[model_name]] for model_name in model_names]
    plt.bar(
        list(model_names.values()),
        [each[model_name] for model_name in model_names],
        color=colors,
    )
    # Set the y range
    plt.ylim(y_range)
    plt.ylabel(
        "Average accuracy over all tests within cutoffs", fontsize=GLOBAL_FONTSIZE
    )
    plt.xticks(fontsize=GLOBAL_FONTSIZE)
    plt.yticks(fontsize=GLOBAL_FONTSIZE)

    # horizontal line at y=0.8
    plt.axhline(y=0.8, color="lightcoral", linestyle="--")

    # save
    plt.savefig(f"{PLOT_DIR}/{name}.png", dpi=300, bbox_inches="tight")
    plt.close()
