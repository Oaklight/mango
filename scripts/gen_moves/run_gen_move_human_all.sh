#!/usr/bin/bash

# given as path of all jericho games folders
# go over each folder and run the gen_move_human.py script on it

# path=${1:-'./data/maps'}
# jericho_path=${2:-'../z-machine-games-master/jericho-game-suite'}
# if not provided, prints the help message
if [ $# -eq 0 ]; then
    echo "Usage: ./run_gen_move_human_all.sh -p <path> -j <jericho_path>"
    exit 1
fi

# parse the arguments
while getopts p:j: flag
do
    case "${flag}" in
        p) path=${OPTARG};;
        j) jericho_path=${OPTARG};;
    esac
done

games=$(ls $path)
for game in $games
do
    valid_moves="$path/$game/$game.valid_moves.csv"
    # skip if this file not exists
    if [ ! -f $valid_moves ]; then
        continue
    else
        python ./src/gen_moves/gen_move_human.py -c $valid_moves -j $jericho_path
    fi
done

echo "Good Job!"