#!/usr/bin/bash

# given as path of all jericho games folders
# go over each folder and run the gen_move_human.py script on it

path=${1:-'./data/maps'}
jericho_env=${2:-'../z-machine-games-master/jericho-game-suite'}
games=$(ls $path)
for game in $games
do
    map_machine="$path/$game/$game.map.machine"
    map_human="$path/$game/$game.map.human"
    # skip if these files not exists
    if [ ! -f $map_machine ] || [ ! -f $map_human ] ; then    
        continue
    else
        python ./src/gen_moves/gen_move_final.py -d $path/$game
    fi
done

echo "Good Job!"