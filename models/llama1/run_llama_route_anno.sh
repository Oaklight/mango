export TARGET_FOLDER=/remote-home/share/llama
export MODEL_SIZE=30B

CUDA_VISIBLE_DEVICES=4,5,6,7 torchrun \
--nproc_per_node 4 --master_port=25641 ./llama_infer_route_anno.py \
--ckpt_dir $TARGET_FOLDER/$MODEL_SIZE \
--tokenizer_path $TARGET_FOLDER/tokenizer.model \
--mango_folder /remote-home/pli/mango \
--save_folder /remote-home/pli/mango/inhouse_llms_results_pli \
--max_batch_size 28 # 4,28