#!/bin/bash

#lgop.z3 error
# path=${1:-'./data/z-machine-games-master/jericho-game-suite'}
if [ $# -eq 0 ]; then
    echo "Usage: ./run_gen_walkthrough_all.sh -j <jericho_path>"
    exit 1
fi

# parse the arguments
while getopts j: flag
do
    case "${flag}" in
        j) jericho_path=${OPTARG};;
    esac
done

files=$(ls $jericho_path)
for filename in $files
do
   echo $filename
   python ./src/gen_moves/gen_walkthrough.py -g $filename \
   -j $jericho_path \
   -odir ./data/maps
done

echo "Good Job!"