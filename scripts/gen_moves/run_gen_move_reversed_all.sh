#!/bin/bash

# path=${1:-'./data/z-machine-games-master/jericho-game-suite'}
if [ $# -eq 0 ]; then
    echo "Usage: ./run_gen_move_reversed_all.sh -j <jericho_path> -i <input_dir> [-g <game_name>]"
    exit 1
fi

# parse the arguments
# while getopts j: flag
# do
#     case "${flag}" in
#         j) jericho_path=${OPTARG};;
#     esac
# done
while getopts j:i:g: flag
do
    case "${flag}" in
        j) jericho_path=${OPTARG};;
        i) input_dir=${OPTARG};;
        g) game_name=${OPTARG};;
    esac
done

# if g not provided, generate for all games
if [ -z "$game_name" ]
then
    echo "Generating for all games..."
    files=$(ls $jericho_path)
    for filename in $files
    do
        echo $filename
        python ./src/gen_moves/gen_move_reversed.py -g $filename \
        -j $jericho_path \
        --max_steps 70 \
        -idir $input_dir \
        -odir $input_dir
        python ./src/gen_moves/gen_move_merge.py -p $input_dir -g $filename
    done
    echo "Good Job!"
fi
# generate for a specific game
echo "Generating for $game_name..."
python ./src/gen_moves/gen_move_reversed.py -g $game_name \
-j $jericho_path \
--max_steps 70 \
-idir $input_dir \
-odir $input_dir
python ./src/gen_moves/gen_move_merge.py -p $input_dir -g $game_name
echo "Good Job!"