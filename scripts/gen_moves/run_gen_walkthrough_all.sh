#!/bin/bash

#lgop.z3 error
path=${1:-'./data/z-machine-games-master/jericho-game-suite'}
files=$(ls $path)
for filename in $files
do
   echo $filename
   python ./src/gen_moves/gen_walkthrough.py -g $filename \
   -j ./data/z-machine-games-master/jericho-game-suite \
   -odir ./data/maps
done

echo "Good Job!"