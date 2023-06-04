#!/bin/bash

# python src/gen_evals/gpt.eval_df_simple.py -r ../gpt-games-results/dragon/results/ --simple -odir ./evals/gpt -g dragon
if [ $# -eq 0 ]; then
    echo "Usage: ./run_eval_route.harsh.sh -m <model_name> -p <path_to_model_results> -g <game> <--harsh || --nice>"
    exit 1
fi

# parse the arguments
while getopts ":m:p:g:nh" opt; do
    case $opt in
        m) model_name="$OPTARG";;
        p) path_to_model_results="$OPTARG";;
        g) game="$OPTARG";;
        n) nice=true;;
        h) harsh=true;;
        \?) echo "Invalid option -$OPTARG" >&2;;
    esac
done

games=$(ls $path_to_model_results)
if [ -z "$game" ]
then
    for game in $games
    do
        # run eval on all games
        if [ -z "$nice" ]
        then
            python src/gen_evals/$model_name.eval_route.py -r $path_to_model_results/$game/results/ -odir ./evals/$model_name/route -g $game
        else
            python src/gen_evals/$model_name.eval_route.py -r $path_to_model_results/$game/results/ --simple -odir ./evals/$model_name/route -g $game
        fi
    done
else
    # run eval on specific game
    if [ -z "$nice" ]
    then
        python src/gen_evals/$model_name.eval_route.py -r $path_to_model_results/$game/results/ -odir ./evals/$model_name/route -g $game
    else
        python src/gen_evals/$model_name.eval_route.py -r $path_to_model_results/$game/results/ --simple -odir ./evals/$model_name/route -g $game
    fi
fi

