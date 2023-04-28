import argparse
from digraph import intuitive_reverse_map
from utils import printColor, inputColor, buildMap


# argparse to read in the map and actions files
# call intuitive_reverse_map with the map and actions files
# write the output to a file

parser = argparse.ArgumentParser()
parser.add_argument('--map', type=str, default='../data/zork1.map')
parser.add_argument('--actions', type=str, default='../data/zork1.actions')
args = parser.parse_args()

printColor(f"processing map: {args.map}, actions: {args.actions}", 'b')
# prompt to confirm before continue
confirm = inputColor("Continue? (y/n) ", 'b', inline=True)
if confirm == "y":
    intuitive_reverse_map(args.map, args.actions)
else:
    printColor("Aborted!", 'b')