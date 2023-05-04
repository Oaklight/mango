#!/usr/bin/bash

# given as path of all jericho games folders
# go over each folder and run the gen_move_human.py script on it

# receives path and game name, they are required parameters
# path is the path to the games folder
# game is the name of the game to run on
# jericho_env is the path to the jericho game suite

# example: ./run_gen_move_human_to_final.sh -p ./data/maps -g adventure -j ../z-machine-games-master/jericho-game-suite

# if not provided, prints the help message
if [ $# -eq 0 ]; then
    echo "Usage: ./run_gen_move_human_to_final.sh -p <path> -g <game> -j <jericho_env>"
    exit 1
fi

# parse the arguments
while getopts p:g:j: flag
do
    case "${flag}" in
        p) path=${OPTARG};;
        g) game_tgt=${OPTARG};;
        j) jericho_env=${OPTARG};;
    esac
done

games=$(ls $path)
# for game in $games check if it matches
for game in $games; do
    if [[ $game != $game_tgt ]]; then
        continue
    fi
    valid_moves="$path/$game/$game.valid_moves.csv"
    # skip if this file not exists
    if [ ! -f $valid_moves ]; then
        continue
    else
        python ./src/gen_moves/gen_move_human.py -c $valid_moves -j $jericho_env
        map_machine="$path/$game/$game.map.machine"
        map_human="$path/$game/$game.map.human"
        if [ ! -f $map_machine ] || [ ! -f $map_human ] ; then
            continue
        else
            python ./src/gen_moves/gen_move_final.py -d $path/$game
        fi
    fi
done

echo "Good Job!"