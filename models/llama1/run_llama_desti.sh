export TARGET_FOLDER=/remote-home/share/llama
export MODEL_SIZE=30B

# CUDA_VISIBLE_DEVICES=0,1,2,3 torchrun \
# --nproc_per_node 4 --master_port=25642 ./llama_infer_desti.py \
# --ckpt_dir $TARGET_FOLDER/$MODEL_SIZE \
# --tokenizer_path $TARGET_FOLDER/tokenizer.model \
# --mango_folder /remote-home/pli/mango \
# --save_folder /remote-home/pli/mango/inhouse_llms_results_pli \
# --start_game_idx 45 \
# --end_game_idx 55 \
# --max_batch_size 2 # 2,28

CUDA_VISIBLE_DEVICES=1,2,5,6 torchrun \
--nproc_per_node 4 --master_port=25642 ./llama_infer_desti.py \
--ckpt_dir $TARGET_FOLDER/$MODEL_SIZE \
--tokenizer_path $TARGET_FOLDER/tokenizer.model \
--mango_folder /remote-home/pli/mango \
--save_folder /remote-home/pli/mango/inhouse_llms_results_pli \
--start_game_idx 45 \
--end_game_idx 55 \
--max_batch_size 2 # 2,28