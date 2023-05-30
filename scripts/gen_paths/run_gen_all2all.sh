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


# GAME RELEASE
# if g not specified, release all games
if [ -z "$game" ]
then
    for game in $games
    do
        # release by copy game.all2all.json, game.code2anno.json, game.anno2code.json, game.walkthrough, game.moves to data/maps/game to release folder
        release_dir="./data/maps-release"
        mkdir -p $release_dir
        # go over each dir in map_path, check if all release file present, then release
        if [ -f "$map_path/$game/$game.all2all.json" ] && [ -f "$map_path/$game/$game.code2anno.json" ] && [ -f "$map_path/$game/$game.anno2code.json" ] && [ -f "$map_path/$game/$game.walkthrough" ] && [ -f "$map_path/$game/$game.moves" ]
        then
            game_release_dir="$release_dir/$game"
            mkdir -p $game_release_dir
            cp "$map_path/$game/$game.all2all.json" "$game_release_dir/$game.all2all.json"
            cp "$map_path/$game/$game.code2anno.json" "$game_release_dir/$game.code2anno.json"
            cp "$map_path/$game/$game.anno2code.json" "$game_release_dir/$game.anno2code.json"
            cp "$map_path/$game/$game.walkthrough" "$game_release_dir/$game.walkthrough"
            cp "$map_path/$game/$game.moves" "$game_release_dir/$game.moves"
            echo "Release $game"
        else
            echo "Missing release files for $game"
        fi
    done
else
    # release by copy game.all2all.json, game.code2anno.json, game.anno2code.json, game.walkthrough, game.moves to data/maps/game to release folder
    release_dir="./data/maps-release"
    mkdir -p $release_dir
    # go over each dir in map_path, check if all release file present, then release
    if [ -f "$map_path/$game/$game.all2all.json" ] && [ -f "$map_path/$game/$game.code2anno.json" ] && [ -f "$map_path/$game/$game.anno2code.json" ] && [ -f "$map_path/$game/$game.walkthrough" ] && [ -f "$map_path/$game/$game.moves" ]
    then
        game_release_dir="$release_dir/$game"
        mkdir -p $game_release_dir
        cp "$map_path/$game/$game.all2all.json" "$game_release_dir/$game.all2all.json"
        cp "$map_path/$game/$game.code2anno.json" "$game_release_dir/$game.code2anno.json"
        cp "$map_path/$game/$game.anno2code.json" "$game_release_dir/$game.anno2code.json"
        cp "$map_path/$game/$game.walkthrough" "$game_release_dir/$game.walkthrough"
        cp "$map_path/$game/$game.moves" "$game_release_dir/$game.moves"
        echo "Release $game"
    else
        echo "Missing release files for $game"
    fi
fi
