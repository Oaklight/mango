#!/bin/bash

# gen_all2all.py [-h] --map MAP (--actions ACTIONS | --reverse_map REVERSE_MAP) [--output_dir OUTPUT_DIR]
if [ $# -eq 0 ]; then
    echo "Usage: ./run_gen_all2all.sh -p <map_path> [-g <game>]"
    exit 1
fi

# parse the arguments
while getopts p:g: flag
do
    case "${flag}" in
        p) map_path=${OPTARG};;
        g) game=${OPTARG};;
    esac
done

games=$(ls $map_path)


if [ -z "$game" ]
then
    for game in $games
    do
        # python src/gen_paths/gen_all2all.py -m ./data/maps/zork3/zork3.map.human -r ./data/maps/zork3/zork3.map.reversed -odir ./data/maps/zork3
        map_human="$map_path/$game/$game.map.human"
        map_reversed="$map_path/$game/$game.map.reversed"
        output_dir="$map_path/$game"
        python src/gen_paths/gen_all2all.py -m $map_human -r $map_reversed -odir $output_dir
    done
else
    map_human="$map_path/$game/$game.map.human"
    map_reversed="$map_path/$game/$game.map.reversed"
    output_dir="$map_path/$game"
    python src/gen_paths/gen_all2all.py -m $map_human -r $map_reversed -odir $output_dir
fi