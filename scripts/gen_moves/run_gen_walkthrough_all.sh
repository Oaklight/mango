#!/bin/bash

#lgop.z3 error
# path=${1:-'./data/z-machine-games-master/jericho-game-suite'}
if [ $# -eq 0 ]; then
    echo "Usage: ./run_gen_walkthrough_all.sh -j <jericho_path> -o <output_dir> [-g <game_name>]"
    exit 1
fi

# # parse the arguments
while getopts j:o:g: flag
do
    case "${flag}" in
        j) jericho_path=${OPTARG};;
        o) output_dir=${OPTARG};;
        g) game_name=${OPTARG};;
    esac
done

# rewrite the bash logic, iter over all games, if game_name provided, skip the rest
games=$(ls $jericho_path)
for game in $games
do
    # process to remove extensions
    game=${game%.*}

    # skip if game name is empty, or game name provided and not equal to game name
    if [ -z "$game_name" ] || [ "$game_name" == "$game" ]
    then
        echo "Generating for $game..."
        python ./src/gen_moves/gen_walkthrough.py -g $game \
        -j $jericho_path \
        -odir $output_dir \
        -acts
    fi
done

echo "Good Job!"