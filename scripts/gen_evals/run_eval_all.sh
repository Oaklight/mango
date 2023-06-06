temp_data=./temp_data
log_data=./logs

# # ================= GPT =================

# infer_data=../gpt-games-results
# eval_path=./evals
# cutoff_json=$eval_path/cutoff_step_fjd.json
# temp_data_this=$temp_data/gpt

# # route
# ./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json -e $eval_path -m gpt4 -h > $log_data/gpt4-harsh-route.log
# ./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json -e $eval_path -m gpt4 -n > $log_data/gpt4-nice-route.log
# ./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json -e $eval_path -m gpt3.5 -h > $log_data/gpt35-harsh-route.log
# ./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json -e $eval_path -m gpt3.5 -n > $log_data/gpt35-nice-route.log

# # desti
# ./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json -e $eval_path -m gpt4 -h > $log_data/gpt4-harsh-desti.log
# ./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json -e $eval_path -m gpt4 -n > $log_data/gpt4-nice-desti.log
# ./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json -e $eval_path -m gpt3.5 -h > $log_data/gpt35-harsh-desti.log
# ./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json -e $eval_path -m gpt3.5 -n > $log_data/gpt35-nice-desti.log


# python src/gen_plots/collect_data.py -e $eval_path -t $temp_data_this

# python src/gen_plots/gpt35_vs_gpt4.py

# python src/gen_plots/gpt.together.py
# python src/gen_plots/gpt.destination.py
# python src/gen_plots/gpt.route.py

# python src/gen_plots/trend_regression.py > $log_data/trend_regression.log

# ================= llama =================

infer_data=../mango-inhouse-llms/llama
eval_path=./evals_llama
cutoff_json=$eval_path/cutoff_step_llama.json
temp_data_this=$temp_data/llama

# route
echo "route"
./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json -e $eval_path -m llama -h
./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json -e $eval_path -m llama -n
# ./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json -e $eval_path -m gpt3.5 -h > $log_data/gpt35-harsh-route.log
# ./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json -e $eval_path -m gpt3.5 -n > $log_data/gpt35-nice-route.log

# desti
echo "desti"
./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json -e $eval_path -m llama -h > $log_data/llama-harsh-desti.log
./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json -e $eval_path -m llama -n > $log_data/llama-nice-desti.log
# ./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json -e $eval_path -m gpt3.5 -h > $log_data/gpt35-harsh-desti.log
# ./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json -e $eval_path -m gpt3.5 -n > $log_data/gpt35-nice-desti.log


python src/gen_plots/collect_data.py -e $eval_path -t $temp_data_this

# python src/gen_plots/gpt35_vs_gpt4.py

# python src/gen_plots/gpt.together.py
# python src/gen_plots/gpt.destination.py
# python src/gen_plots/gpt.route.py

# python src/gen_plots/trend_regression.py > trend_regression.log