#!/bin/bash

path=${1:-'./data/z-machine-games-master/jericho-game-suite'}
files=$(ls $path)
for filename in $files
do
   echo $filename
   python ./src/gen_moves/gen_move_reversed.py -g $filename \
   -j ./data/z-machine-games-master/jericho-game-suite \
   --max_steps 70 \
   -idir ./data/maps \
   -odir ./data/maps
done

echo "Good Job!"