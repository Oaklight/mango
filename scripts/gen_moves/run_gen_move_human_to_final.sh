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
    echo "Usage: ./run_gen_move_human_to_final.sh -p <path> -j <jericho_env> [-g <game>]"
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


# generate for a specific game
function generate_for_game {
    echo "Generating for $1..."
    valid_moves="$path/$1/$1.valid_moves.csv"
    # skip if this file not exists
    if [ ! -f $valid_moves ]; then
        echo "File $valid_moves not exists"
        exit 1
    else
        python ./src/gen_moves/gen_move_human.py -c $valid_moves -j $jericho_env
        map_machine="$path/$1/$1.map.machine"
        map_human="$path/$1/$1.map.human"
        if [ ! -f $map_machine ] || [ ! -f $map_human ] ; then
            echo "File $map_machine or $map_human not exists"
            exit 1
        else
            python ./src/gen_moves/gen_move_final.py -d $path/$1
        fi
        # check if anno2code.json and code2anno.json exist after previous line, if not, then the annotation is not resolved. map.human should be removed until the annotation is resolved
        anno2code="$path/$1/anno2code.json"
        code2anno="$path/$1/code2anno.json"
        if [ ! -f $anno2code ] || [ ! -f $code2anno ] ; then
            echo "File $anno2code or $code2anno not exists"
            rm $map_human
        fi
    fi
}


# use it directly if g not provided
if [ -z "$game_tgt" ]
then
    echo "Generating for all games..."
    games=$(ls $path)
    for game in $games; do
        generate_for_game $game
    done
    echo "Done for all games!"
else
    echo "Generating for $game_tgt..."
    generate_for_game $game_tgt
    echo "Done for $game_tgt!"
fi