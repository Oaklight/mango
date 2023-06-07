temp_data=./temp_data
log_data=./logs

# ================= GPT =================

# infer_data=../gpt-games-results
# eval_path=./evals
# temp_data_this=$temp_data/gpt

# python src/gen_evals/get_cutoff_fjd.py
# cutoff_json=$eval_path/cutoff_step_fjd.json

# echo "route gpt4"
# ./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json -e $eval_path -m gpt4 -h > $log_data/gpt4-harsh-route.log
# ./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json -e $eval_path -m gpt4 -n > $log_data/gpt4-nice-route.log
# echo "route gpt3.5"
# ./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json -e $eval_path -m gpt3.5 -h > $log_data/gpt35-harsh-route.log
# ./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json -e $eval_path -m gpt3.5 -n > $log_data/gpt35-nice-route.log

# echo "desti gpt4"
# ./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json -e $eval_path -m gpt4 -h > $log_data/gpt4-harsh-desti.log
# ./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json -e $eval_path -m gpt4 -n > $log_data/gpt4-nice-desti.log
# echo "desti gpt3.5"
# ./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json -e $eval_path -m gpt3.5 -h > $log_data/gpt35-harsh-desti.log
# ./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json -e $eval_path -m gpt3.5 -n > $log_data/gpt35-nice-desti.log

# echo "collect data"
# python src/gen_plots/collect_data.py -e $eval_path -t $temp_data_this

# echo "plot gpt4 vs gpt3.5"
# python src/gen_plots/gpt35_vs_gpt4.py

# echo "plot scoreboards"
# python src/gen_plots/gpt.together.py
# python src/gen_plots/gpt.destination.py
# python src/gen_plots/gpt.route.py

# echo "plot trend & error bars"
# python src/gen_plots/trend_regression.py > $log_data/trend_regression.log

# # ================= llama =================

# infer_data=../mango-inhouse-llms/llama
# eval_path=./evals_llama
# temp_data_this=./$temp_data/llama

# python src/gen_evals/get_cutoff.py -i $infer_data -e $eval_path -t "path_gen_llama" -m "llama"
# python src/gen_evals/get_cutoff.py -i $infer_data -e $eval_path -t "path_gen_llama_anno" -m "llama_anno"
# cutoff_json_original=$eval_path/cutoff_step_llama.json
# cutoff_json_anno=$eval_path/cutoff_step_llama_anno.json


# echo "route llama"
# ./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json_original -e $eval_path -m llama -h > $log_data/llama-harsh-route.log
# ./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json_original -e $eval_path -m llama -n > $log_data/llama-nice-route.log
# echo "desti llama"
# ./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json_original -e $eval_path -m llama -h > $log_data/llama-harsh-desti.log
# ./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json_original -e $eval_path -m llama -n > $log_data/llama-nice-desti.log

# echo "route llama_anno"
# ./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json_anno -e $eval_path -m llama_anno -h > $log_data/llama_anno-harsh-route.log
# ./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json_anno -e $eval_path -m llama_anno -n > $log_data/llama_anno-nice-route.log
# echo "desti llama_anno"
# ./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json_anno -e $eval_path -m llama_anno -h > $log_data/llama_anno-harsh-desti.log
# ./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json_anno -e $eval_path -m llama_anno -n > $log_data/llama_anno-nice-desti.log

# python src/gen_plots/collect_data.py -e $eval_path -t $temp_data_this

# python src/gen_plots/gpt35_vs_gpt4.py

# python src/gen_plots/gpt.together.py
# python src/gen_plots/gpt.destination.py
# python src/gen_plots/gpt.route.py

# python src/gen_plots/trend_regression.py > trend_regression.log

# ================= rwkv =================












# # ================= plot =================
# python src/gen_plots/avg_acc.together.py

# ================= gpt at llama cutoffs =================
echo "gpt at min(llama, gpt) cutoffs"
infer_data=../gpt-games-results
cross_eval_path=./evals_gpt@llama
temp_data_this=$temp_data/gpt@llama

mkdir -p $cross_eval_path

llama_path=./evals_llama
gpt_path=./evals
cutoff_json_llama=$llama_path/cutoff_step_llama.json
cutoff_json_gpt=$gpt_path/cutoff_step_fjd.json
python src/gen_evals/min_cutoff.py -c1 $cutoff_json_llama -c2 $cutoff_json_gpt -o $cross_eval_path/cutoff_step_gpt_llama.json
cutoff_json_across=$cross_eval_path/cutoff_step_gpt_llama.json

echo "route gpt4"
./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m gpt4 -h > $log_data/gpt4-harsh-route.log
./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m gpt4 -n > $log_data/gpt4-nice-route.log
echo "route gpt3.5"
./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m gpt3.5 -h > $log_data/gpt35-harsh-route.log
./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m gpt3.5 -n > $log_data/gpt35-nice-route.log

echo "desti gpt4"
./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m gpt4 -h > $log_data/gpt4-harsh-desti.log
./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m gpt4 -n > $log_data/gpt4-nice-desti.log
echo "desti gpt3.5"
./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m gpt3.5 -h > $log_data/gpt35-harsh-desti.log
./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m gpt3.5 -n > $log_data/gpt35-nice-desti.log

echo "collect data"
sleep 3
python src/gen_plots/collect_data.py -e $cross_eval_path -t $temp_data_this


# ================= gpt at llama_anno cutoffs =================
echo "gpt at min(gpt, llama_anno) cutoffs"
infer_data=../gpt-games-results
cross_eval_path=./evals_gpt@llama_anno
temp_data_this=$temp_data/gpt@llama_anno

mkdir -p $cross_eval_path

llama_path=./evals_llama
gpt_path=./evals
cutoff_json_llama=$llama_path/cutoff_step_llama_anno.json
cutoff_json_gpt=$gpt_path/cutoff_step_fjd.json
python src/gen_evals/min_cutoff.py -c1 $cutoff_json_llama -c2 $cutoff_json_gpt -o $cross_eval_path/cutoff_step_gpt_llama_anno.json
cutoff_json_across=$cross_eval_path/cutoff_step_gpt_llama_anno.json

echo "route gpt4"
./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m gpt4 -h > $log_data/gpt4@llama_anno-harsh-route.log
./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m gpt4 -n > $log_data/gpt4@llama_anno-nice-route.log
echo "route gpt3.5"
./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m gpt3.5 -h > $log_data/gpt35@llama_anno-harsh-route.log
./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m gpt3.5 -n > $log_data/gpt35@llama_anno-nice-route.log

echo "desti gpt4"
./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m gpt4 -h > $log_data/gpt4@llama_anno-harsh-desti.log
./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m gpt4 -n > $log_data/gpt4@llama_anno-nice-desti.log
echo "desti gpt3.5"
./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m gpt3.5 -h > $log_data/gpt35@llama_anno-harsh-desti.log
./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m gpt3.5 -n > $log_data/gpt35@llama_anno-nice-desti.log

echo "collect data"
sleep 3
python src/gen_plots/collect_data.py -e $cross_eval_path -t $temp_data_this

# ================= llama at gpt cutoffs =================
echo "llama at min(gpt, llama) cutoffs"
infer_data=../mango-inhouse-llms/llama
cross_eval_path=./evals_llama@gpt
temp_data_this=$temp_data/llama@gpt

mkdir -p $cross_eval_path

llama_path=./evals_llama
gpt_path=./evals
cutoff_json_llama=$llama_path/cutoff_step_llama.json
cutoff_json_gpt=$gpt_path/cutoff_step_fjd.json
python src/gen_evals/min_cutoff.py -c1 $cutoff_json_llama -c2 $cutoff_json_gpt -o $cross_eval_path/cutoff_step_gpt_llama.json
cutoff_json_across=$cross_eval_path/cutoff_step_gpt_llama.json

echo "route llama"
./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m llama -h > $log_data/llama@gpt-harsh-route.log
./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m llama -n > $log_data/llama@gpt-nice-route.log
# echo "route llama_anno"
# ./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m llama_anno -h > $log_data/llama_anno-harsh-route.log
# ./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m llama_anno -n > $log_data/llama_anno-nice-route.log

echo "desti llama"
./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m llama -h > $log_data/llama@gpt-harsh-desti.log
./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m llama -n > $log_data/llama@gpt-nice-desti.log
# echo "desti llama_anno"
# ./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m llama_anno -h > $log_data/llama_anno-harsh-desti.log
# ./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m llama_anno -n > $log_data/llama_anno-nice-desti.log

echo "collect data"
sleep 3
python src/gen_plots/collect_data.py -e $cross_eval_path -t $temp_data_this

# ================= llama_anno at gpt cutoffs =================
echo "llama at min(gpt, llama_anno) cutoffs"
infer_data=../mango-inhouse-llms/llama
cross_eval_path=./evals_llama_anno@gpt
temp_data_this=$temp_data/llama_anno@gpt

mkdir -p $cross_eval_path

llama_path=./evals_llama
gpt_path=./evals
cutoff_json_llama=$llama_path/cutoff_step_llama_anno.json
cutoff_json_gpt=$gpt_path/cutoff_step_fjd.json
python src/gen_evals/min_cutoff.py -c1 $cutoff_json_llama -c2 $cutoff_json_gpt -o $cross_eval_path/cutoff_step_gpt_llama_anno.json
cutoff_json_across=$cross_eval_path/cutoff_step_gpt_llama_anno.json

echo "route llama anno"
# ./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m llama -h > $log_data/llama-harsh-route.log
# ./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m llama -n > $log_data/llama-nice-route.log
# echo "route llama_anno"
./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m llama_anno -h > $log_data/llama_anno@gpt-harsh-route.log
./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m llama_anno -n > $log_data/llama_anno@gpt-nice-route.log

echo "desti llama anno"
# ./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m llama -h > $log_data/llama-harsh-desti.log
# ./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m llama -n > $log_data/llama-nice-desti.log
# echo "desti llama_anno"
./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m llama_anno -h > $log_data/llama_anno@gpt-harsh-desti.log
./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m llama_anno -n > $log_data/llama_anno@gpt-nice-desti.log

echo "collect data"
sleep 3
python src/gen_plots/collect_data.py -e $cross_eval_path -t $temp_data_this

# ================= llama at llama_anno cutoffs =================
echo "llama at min(llama, llama_anno) cutoffs"
infer_data=../mango-inhouse-llms/llama
cross_eval_path=./evals_llama@llama_anno
temp_data_this=$temp_data/llama@llama_anno

mkdir -p $cross_eval_path

llama_path=./evals_llama
llama_anno_path=./evals_llama
cutoff_json_llama=$llama_path/cutoff_step_llama.json
cutoff_json_llama_anno=$llama_anno_path/cutoff_step_llama_anno.json
python src/gen_evals/min_cutoff.py -c1 $cutoff_json_llama -c2 $cutoff_json_llama_anno -o $cross_eval_path/cutoff_step_llama_llama_anno.json
cutoff_json_across=$cross_eval_path/cutoff_step_llama_llama_anno.json

echo "route llama"
./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m llama -h > $log_data/llama@llama_anno-harsh-route.log
./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m llama -n > $log_data/llama@llama_anno-nice-route.log

echo "desti llama"
./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m llama -h > $log_data/llama@llama_anno-harsh-desti.log
./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m llama -n > $log_data/llama@llama_anno-nice-desti.log

echo "collect data"
sleep 3
python src/gen_plots/collect_data.py -e $cross_eval_path -t $temp_data_this

# ================= llama_anno at llama cutoffs =================
echo "llama_anno at min(llama, llama_anno) cutoffs"
infer_data=../mango-inhouse-llms/llama
cross_eval_path=./evals_llama_anno@llama
temp_data_this=$temp_data/llama_anno@llama

mkdir -p $cross_eval_path

llama_path=./evals_llama
llama_anno_path=./evals_llama
cutoff_json_llama=$llama_path/cutoff_step_llama.json
cutoff_json_llama_anno=$llama_anno_path/cutoff_step_llama_anno.json
python src/gen_evals/min_cutoff.py -c1 $cutoff_json_llama -c2 $cutoff_json_llama_anno -o $cross_eval_path/cutoff_step_llama_llama_anno.json
cutoff_json_across=$cross_eval_path/cutoff_step_llama_llama_anno.json

echo "route llama_anno"
./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m llama_anno -h > $log_data/llama_anno@llama-harsh-route.log
./scripts/gen_evals/run_eval_route.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m llama_anno -n > $log_data/llama_anno@llama-nice-route.log

echo "desti llama_anno"
./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m llama_anno -h > $log_data/llama_anno@llama-harsh-desti.log
./scripts/gen_evals/run_eval_desti.sh -p $infer_data -c $cutoff_json_across -e $cross_eval_path -m llama_anno -n > $log_data/llama_anno@llama-nice-desti.log

echo "collect data"
sleep 3
python src/gen_plots/collect_data.py -e $cross_eval_path -t $temp_data_this
