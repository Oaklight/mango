import matplotlib.pyplot as plt
import numpy as np
from colors import COLOR_MAP

# Dummy data for model names
model_names = {
    "BLOOM": "bloom",
    "LLaMA": "llama",
    "RWKV": "rwkv",
    "GPT-3.5-turbo": "gpt3.5",
    "GPT-4": "gpt4",
}

# Dummy data for average accuracies
avg_acc_DF = {
    "GPT-3.5-turbo": 0.85,
    "GPT-4": 0.92,
    "RWKV": 0.78,
    "LLaMA": 0.89,
    "BLOOM": 0.95,
}

# Create the bar plot
colors = [COLOR_MAP[model_names[model_name]] for model_name in model_names]
plt.bar(list(model_names.keys()), [avg_acc_DF[model_name] for model_name in model_names], color=colors)

plt.ylabel("average accurcy of destination finding")

# Adjust the layout to prevent overlapping of labels
plt.tight_layout()

# Save the plot as a PNG file
png_path = "./evals/avg_acc_destination.png"
plt.savefig(png_path, bbox_inches='tight', dpi=300)

# Show the plot
plt.show()
