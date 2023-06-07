# this function serves to compute the min cutoffs from two given reference cutoff files.

import argparse
import json
import os

parser = argparse.ArgumentParser()
parser.add_argument("--cutoff1", "-c1", type=str, required=True)
parser.add_argument("--cutoff2", "-c2", type=str, required=True)
parser.add_argument("--output", "-o", type=str, required=True)
args = parser.parse_args()

# assert cutoff1 and cutoff2 existance
assert os.path.exists(args.cutoff1), f"{args.cutoff1} does not exist"
assert os.path.exists(args.cutoff2), f"{args.cutoff2} does not exist"

# read cutoff1 and cutoff2, they are json
with open(args.cutoff1, "r") as f:
    cutoff1 = json.load(f)
with open(args.cutoff2, "r") as f:
    cutoff2 = json.load(f)

# compute both presented games
games1 = set(cutoff1.keys())
games2 = set(cutoff2.keys())
games_common = games1.intersection(games2)

# compute min cutoffs
min_cutoffs = {}
for game in games_common:
    min_cutoffs[game] = min(int(cutoff1[game]), int(cutoff2[game]))

# write min cutoffs to file
with open(args.output, "w") as f:
    json.dump(min_cutoffs, f, indent=4, sort_keys=True)
