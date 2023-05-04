#!/usr/bin/bash

# given as path of all jericho games folders
# go over each folder and run the gen_move_human.py script on it

path=${1:-'./data/maps'}
jericho_env=${2:-'../z-machine-games-master/jericho-game-suite'}
games=$(ls $path)
for game in $games
do
    valid_moves="$path/$game/$game.valid_moves.csv"
    # skip if this file not exists
    if [ ! -f $valid_moves ]; then
        continue
    fi
    python ./src/gen_moves/gen_move_human.py -c $valid_moves -j $jericho_env
done

echo "Good Job!"