#!/bin/bash

#lgop.z3 unsupportedGameWarning
#theatre env.get_player_location() == None
# path=${1:-'./data/z-machine-games-master/jericho-game-suite'}
if [ $# -eq 0 ]; then
    echo "Usage: ./run_gen_move_machine_all.sh -j <jericho_path> -o <output_dir> [-g <game_name>] [-s <max_steps>] [-a]"
    exit 1
fi

# parse the arguments
while getopts j:o:g:s:a opt
do
    case $opt in
        j) jericho_path="$OPTARG";;
        o) output_dir="$OPTARG";;
        g) game_name="$OPTARG";;
        s) max_steps="$OPTARG";;
        a) walk_acts="true";;
    esac
done

if [ -z "$max_steps" ]
then
    max_steps=70
fi

# rewrite the bash logic, iter over all games, if game_name provided, skip the rest
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
            python ./src/gen_moves/gen_move_machine.py -g $game \
            -j $jericho_path \
            --max_steps $max_steps \
            -odir $output_dir
        else
            echo "Generating for $game..."
            python ./src/gen_moves/gen_move_machine.py -g $game \
            -j $jericho_path \
            --max_steps $max_steps \
            -odir $output_dir \
            -acts
        fi
    fi
done

echo "Good Job!"