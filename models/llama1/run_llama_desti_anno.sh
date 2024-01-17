export TARGET_FOLDER=/remote-home/share/llama
export MODEL_SIZE=30B

# CUDA_VISIBLE_DEVICES=4,5,6,7 torchrun \
# --nproc_per_node 4 --master_port=25643 ./llama_infer_desti_anno.py \
# --ckpt_dir $TARGET_FOLDER/$MODEL_SIZE \
# --tokenizer_path $TARGET_FOLDER/tokenizer.model \
# --mango_folder /remote-home/pli/mango \
# --save_folder /remote-home/pli/mango/inhouse_llms_results_pli \
# --start_game_idx 0 \
# --end_game_idx 10000 \
# --max_batch_size 26 # 4,26,28 \

CUDA_VISIBLE_DEVICES=0,1,2,3 torchrun \
--nproc_per_node 4 --master_port=25643 ./llama_infer_desti_anno.py \
--ckpt_dir $TARGET_FOLDER/$MODEL_SIZE \
--tokenizer_path $TARGET_FOLDER/tokenizer.model \
--mango_folder /remote-home/pli/mango \
--save_folder /remote-home/pli/mango/inhouse_llms_results_pli \
--start_game_idx 46 \
--end_game_idx 49 \
--max_batch_size 2 # 4,26,28 \