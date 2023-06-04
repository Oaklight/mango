#!/bin/bash

# python src/gen_evals/gpt.eval_df_simple.py -r ../gpt-games-results/dragon/results/ -odir ./evals/gpt -g dragon
if [ $# -eq 0 ]; then
    # echo "Usage: ./run_eval_desti.harsh.sh -m <model_name> -p <path_to_model_results> -g <game>"
    # how may I have a toggle for --simple?
    # how may I have a toggle for --harsh?
    # how may I have a toggle for --nice?
    echo "Usage: ./run_eval_desti.harsh.sh -m <model_name> -p <path_to_model_results> -g <game> <--harsh || --nice>"
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
        # run on harsh mode if --harsh is specified
        if [ -z "$nice" ]
        then
            python src/gen_evals/$model_name.eval_desti.py -r $path_to_model_results/$game/results/ -odir ./evals/$model_name/desti -g $game
        else
            python src/gen_evals/$model_name.eval_desti.py -r $path_to_model_results/$game/results/ --simple -odir ./evals/$model_name/desti -g $game
        fi
    done
else
    # run eval on specific game
    # run on harsh mode if --harsh is specified
    if [ -z "$nice" ]
    then
        python src/gen_evals/$model_name.eval_desti.py -r $path_to_model_results/$game/results/ -odir ./evals/$model_name/desti -g $game
    else
        python src/gen_evals/$model_name.eval_desti.py -r $path_to_model_results/$game/results/ --simple -odir ./evals/$model_name/desti -g $game
    fi
fi

