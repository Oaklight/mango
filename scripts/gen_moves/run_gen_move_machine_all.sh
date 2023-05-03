#!/bin/bash

#lgop.z3 unsupportedGameWarning
#theatre env.get_player_location() == None
path=${1:-'./data/z-machine-games-master/jericho-game-suite'}
files=$(ls $path)
for filename in $files
do
   echo $filename
   python ./src/gen_moves/gen_move_machine.py -g $filename \
   -j ./data/z-machine-games-master/jericho-game-suite \
   --max_steps 70 \
   -odir ./data/maps
done

echo "Good Job!"