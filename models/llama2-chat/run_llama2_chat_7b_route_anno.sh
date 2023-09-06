export TARGET_FOLDER=/remote-home/share/llama_v2
export MODEL_NAME=llama-2-7b-chat

CUDA_VISIBLE_DEVICES=6 nohup torchrun \
--nproc_per_node 1 --master_port 22345 ./llama2_chat_infer_route_anno.py \
--ckpt_dir $TARGET_FOLDER/$MODEL_NAME \
--tokenizer_path $TARGET_FOLDER/tokenizer.model \
--mango_folder /remote-home/pli/mango \
--save_folder /remote-home/pli/mango/model_results/llama2_chat_7b_results_0723 \
--max_batch_size 4 > ../outs/llama2_chat_7b_route_anno_a800.out 2>&1 & # 2, 28