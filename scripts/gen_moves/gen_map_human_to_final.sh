#!/bin/bash

# given as output_dir of all jericho games folders
# go over each folder and run the gen_move_human.py script on it

# receives output_dir and game name, they are required parameters
# output_dir is the output_dir to the games folder
# game is the name of the game to run on
# jericho_path is the output_dir to the jericho game suite

# example: ./gen_map_human_to_final.sh -p ./data/maps -g adventure -j ../z-machine-games-master/jericho-game-suite

# if not provided, prints the help message
if [ $# -eq 0 ]; then
    echo "Usage: ./gen_map_human_to_final.sh -j <jericho_path> -o <output_dir> [-g <game_name>] [-s <max_step>]"
    exit 1
fi

# parse the arguments
while getopts j:o:g:s: opt
do
    case $opt in
        j) jericho_path="$OPTARG";;
        o) output_dir="$OPTARG";;
        g) game_name="$OPTARG";;
        s) max_step="$OPTARG";;
    esac
done

if [ -z "$max_step" ]
then
    max_step=70
fi

# generate for a specific game
function generate_for_game {
    echo "Generating for $1..."
    valid_moves="$output_dir/$1/$1.valid_moves.csv"
    # skip if this file not exists
    if [ ! -f $valid_moves ]; then
        echo "File $valid_moves not exists"
    else
        python ./src/gen_moves/gen_move_human.py -c $valid_moves -j $jericho_path -s $max_step -acts

        map_machine="$output_dir/$1/$1.map.machine"
        map_human="$output_dir/$1/$1.map.human"
        if [ ! -f $map_machine ] || [ ! -f $map_human ] ; then
            echo "File $map_machine or $map_human not exists"
        else
            python ./src/gen_moves/gen_move_final.py -d $output_dir/$1 -s $max_step
            # check if anno2code.json and code2anno.json exist after previous line, if not, then the annotation is not resolved. map.human should be removed until the annotation is resolved
            anno2code="$output_dir/$1/$1.anno2code.json"
            code2anno="$output_dir/$1/$1.code2anno.json"
            if [ ! -f $anno2code ] || [ ! -f $code2anno ] ; then
                echo "File $anno2code or $code2anno not exists"
                rm $map_human
                # remove anno2code and code2anno if exists
                if [ -f $anno2code ]; then
                    rm $anno2code
                fi
                if [ -f $code2anno ]; then
                    rm $code2anno
                fi
            fi
        fi
    fi
}


# use it directly if g not provided
if [ -z "$game_name" ]
then
    echo "Generating for all games..."
    games=$(ls $output_dir)
    for game in $games; do
        generate_for_game $game
    done
    echo "Done for all games!"
else
    echo "Generating for $game_name..."
    generate_for_game $game_name
    echo "Done for $game_name!"
fi