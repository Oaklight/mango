#!/bin/bash

# python src/gen_evals/gpt.eval_df_simple.py -r ../gpt-games-results/dragon/results/ -odir ./evals/gpt -g dragon
if [ $# -eq 0 ]; then
    echo "Usage: ./run_simple_eval_desti.sh -m <model_name> -p <path_to_model_results> -g <game>"
    exit 1
fi

# parse the arguments
while getopts ":m:p:g:" opt; do
    case $opt in
        m) model_name="$OPTARG";;
        p) path_to_model_results="$OPTARG";;
        g) game="$OPTARG";;
        \?) echo "Invalid option -$OPTARG" >&2;;
    esac
done

games=$(ls $path_to_model_results)
if [ -z "$game" ]
then
    for game in $games
    do
        # run eval on all games
        python src/gen_evals/$model_name.eval_desti.py -r $path_to_model_results/$game/results/ -odir ./evals/$model_name -g $game
    done
else
    # run eval on specific game
    python src/gen_evals/$model_name.eval_desti.py -r $path_to_model_results/$game/results/ -odir ./evals/$model_name -g $game
fi

