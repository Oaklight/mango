#!/bin/bash

# path=${1:-'./data/z-machine-games-master/jericho-game-suite'}
if [ $# -eq 0 ]; then
    echo "Usage: ./gen_map_reversed_all.sh -j <jericho_path> -o <output_dir> [-g <game_name>] [-s <max_steps>]"
    exit 1
fi

# parse the arguments
# while getopts j: flag
# do
#     case "${flag}" in
#         j) jericho_path=${OPTARG};;
#     esac
# done
while getopts j:o:g:s: opt
do
    case $opt in
        j) jericho_path=${OPTARG};;
        o) output_dir=${OPTARG};;
        g) game_name=${OPTARG};;
        s) max_steps="$OPTARG";;
    esac
done

echo "game_name" $game_name
echo "max_steps" $max_steps

if [ -z "$max_steps" ]
then
    max_steps=70
fi

games=$(ls $jericho_path)
for game in $games
do
    # process to remove extensions
    game=${game%.*}
    
    # skip if game name is empty, or game name provided and not equal to game name
    if [ -z "$game_name" ] || [ "$game_name" == "$game" ]
    then
        echo "Generating for $game..."
        python ./src/gen_moves/gen_move_reversed.py -g $game \
        -j $jericho_path \
        --max_steps $max_steps \
        -odir $output_dir \
        -acts
        # python ./src/gen_moves/gen_move_merge.py -p $output_dir -g $game
    fi
done
