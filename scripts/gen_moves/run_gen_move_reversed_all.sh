#!/bin/bash

# path=${1:-'./data/z-machine-games-master/jericho-game-suite'}
if [ $# -eq 0 ]; then
    echo "Usage: ./run_gen_move_reversed_all.sh -j <jericho_path> -i <input_dir> [-g <game_name>] [-a]"
    exit 1
fi

# parse the arguments
# while getopts j: flag
# do
#     case "${flag}" in
#         j) jericho_path=${OPTARG};;
#     esac
# done
while getopts j:i:g:a flag
do
    case "${flag}" in
        j) jericho_path=${OPTARG};;
        i) input_dir=${OPTARG};;
        g) game_name=${OPTARG};;
        a) walk_acts="true";;
    esac
done

games=$(ls $jericho_path)
for game in $games
do
    # process to remove extensions
    game=${game%.*}
    
    # skip if game name is empty, or game name provided and not equal to game name
    if [ -z "$game_name" ] || [ "$game_name" == "$game" ]
    then
        if [ -z "$walk_acts" ]
        then
            echo "Generating for $game..."
            python ./src/gen_moves/gen_move_reversed.py -g $game \
            -j $jericho_path \
            --max_steps 70 \
            -idir $input_dir \
            -odir $input_dir
        else
            echo "Generating for $game..."
            python ./src/gen_moves/gen_move_reversed.py -g $game \
            -j $jericho_path \
            --max_steps 70 \
            -idir $input_dir \
            -odir $input_dir \
            -acts
        fi
        python ./src/gen_moves/gen_move_merge.py -p $input_dir -g $game
    fi
done
