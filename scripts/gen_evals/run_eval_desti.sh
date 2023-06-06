#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: ./run_eval_desti.harsh.sh -m <model_name> -p <path_to_model_results> -g <game> -c <cutoff_json> -e <evals> <-h(ash) || -n(ice)>"
    exit 1
fi

# parse the arguments
while getopts ":m:p:g:c:e:hn" opt; do
    case $opt in
        m) model_name="$OPTARG";;
        p) path_to_model_results="$OPTARG";;
        g) game="$OPTARG";;
        c) cutoff_json="$OPTARG";;
        e) evals="$OPTARG";;
        h) harsh=true;;
        n) nice=true;;
        \?) echo "Invalid option -$OPTARG" >&2;;
    esac
done

games=$(ls $path_to_model_results)
if [ -z "$game" ]
then
    for game in $games
    do
        # run eval on all games
        if [ -z "$nice" ] # if nice is not set
        then
            python src/gen_evals/$model_name.eval_desti.py -r $path_to_model_results/$game/results/ -odir ./$evals/$model_name/desti -c $cutoff_json -g $game
        else
            python src/gen_evals/$model_name.eval_desti.py -r $path_to_model_results/$game/results/ --simple -odir ./$evals/$model_name/desti -c $cutoff_json -g $game
        fi
    done
else
    # run eval on specific game
    if [ -z "$nice" ] # if nice is not set
    then
        python src/gen_evals/$model_name.eval_desti.py -r $path_to_model_results/$game/results/ -odir ./$evals/$model_name/desti -c $cutoff_json -g $game
    else
        python src/gen_evals/$model_name.eval_desti.py -r $path_to_model_results/$game/results/ --simple -odir ./$evals/$model_name/desti -c $cutoff_json -g $game
    fi
fi

