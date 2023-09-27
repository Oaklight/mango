import os
import numpy as np
import matplotlib.pyplot as plt

COLOR_MAP = {
    # "gpt4": "#4682B4",  # steel blue (dark blue)
    "gpt4": "#0000FF",  # blue (blue)
    "gpt3.5": "#6495ED",  # cornflower blue (light blue)
    "rwkv": "#50C878",  # emerald green (light green)
    "rwkv_anno": "#98FF98",  # mint green (light green)
    "llama": "#fdbe38",  # yellow (yellow)
    "llama_anno": "#FFD700",  # gold (light yellow)
    "bloom": "#E0B0FF",  # mauve (light purple)
    "bloom_anno": "#E0B0FF",  # mauve (light purple)
    "random": "gray",

    "GPT-4": "#0000FF",  # blue (blue)
    "GPT-3.5": "#6495ED",  # cornflower blue (light blue)
    "RWKV": "#50C878",  # emerald green (light green)
    "RWKV-S": "#98FF98",  # mint green (light green)
    "LLaMa2": "#fdbe38",  # yellow (yellow)
    "LLaMa2-S": "#FFD700",  # gold (light yellow)
    "LLaMa": "#E0B0FF",  # mauve (light purple)
    "LLaMa-S": "purple",  # purple
}
GLOBAL_FONTSIZE = 40

custom_labels = ["GPT-3.5","GPT-4"]
without_map = [0.09, 0.54]
with_map = [0.38, 0.70]

x = np.arange(2)
total_width, n = 0.7, 2
width = total_width / n
x = x - (total_width - width) / 2

fig = plt.figure(figsize=(16, 16))
plt.tight_layout()
plt.bar(x, without_map,  width=width, label='without small local map', alpha=0.7)
plt.bar(x + width, with_map, width=width, label='with small local map', alpha=0.7)
plt.legend(fontsize=GLOBAL_FONTSIZE+5)
plt.show()

for a,b in zip(x, without_map):
    plt.text(a, b,
             b,
             ha='center', 
             va='bottom', fontsize=GLOBAL_FONTSIZE
            )

for a,b in zip(x + width, with_map):
    plt.text(a, b,
             b,
             ha='center', 
             va='bottom', fontsize=GLOBAL_FONTSIZE
            )

y_range=(0,1)
plt.ylim(y_range)
plt.yticks(fontsize=GLOBAL_FONTSIZE)
plt.xticks(x + width/2, custom_labels, fontsize=GLOBAL_FONTSIZE)

plt.ylabel('Success Rate',fontsize=GLOBAL_FONTSIZE)
plt.axhline(y=0.2, color="lightcoral", linestyle="--")
plt.axhline(y=0.4, color="lightcoral", linestyle="--")
plt.axhline(y=0.6, color="lightcoral", linestyle="--")
plt.axhline(y=0.8, color="lightcoral", linestyle="--")
plt.savefig(f"play_game_results.pdf", dpi=300, bbox_inches="tight")
plt.close()
