#!/bin/bash

#lgop.z3 unsupportedGameWarning
#theatre env.get_player_location() == None
# path=${1:-'./data/z-machine-games-master/jericho-game-suite'}
if [ $# -eq 0 ]; then
    echo "Usage: ./run_gen_move_machine_all.sh -j <jericho_path> -o <output_dir> [-g <game>] [-s <max_steps>]"
    exit 1
fi

# parse the arguments
while getopts ":j:o:g:s:" opt; do
    case $opt in
        j) jericho_path="$OPTARG";;
        o) output_dir="$OPTARG";;
        g) game_tgt="$OPTARG";;
        s) max_steps="$OPTARG";;
        \?) echo "Invalid option -$OPTARG" >&2;;
    esac
done

if [ -z "$max_steps" ]
then
    max_steps=70
fi

# files=$(ls $jericho_path)
# for filename in $files
# do
#    echo $filename
#    python ./src/gen_moves/gen_move_machine.py -g $filename \
#    -j $jericho_path \
#    --max_steps 70 \
#    -odir ./data/maps
# done

# echo "Good Job!"

# if g not provided, generate for all games
if [ -z "$game_tgt" ]
then
    echo "Generating for all games..."
    games=$(ls $jericho_path)
    for game in $games
    do
        echo "Generating for $game..."
        python ./src/gen_moves/gen_move_machine.py -g $game \
        -j $jericho_path \
        --max_steps $max_steps \
        -odir $output_dir
    done
else
    echo "Generating for $game_tgt..."
    python ./src/gen_moves/gen_move_machine.py -g $game_tgt \
    -j $jericho_path \
    --max_steps $max_steps \
    -odir $output_dir
fi
