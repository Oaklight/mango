export TARGET_FOLDER=/remote-home/share/llama_v2
export MODEL_NAME=llama-2-7b

CUDA_VISIBLE_DEVICES=3 nohup torchrun \
--nproc_per_node 1 --master_port 12347 ./llama2_infer_desti.py \
--ckpt_dir $TARGET_FOLDER/$MODEL_NAME \
--tokenizer_path $TARGET_FOLDER/tokenizer.model \
--mango_folder /remote-home/pli/mango \
--save_folder /remote-home/pli/mango/model_results/llama2_7b_results_0723 \
--max_batch_size 4 > ../outs/llama2_7b_desti_a800.out 2>&1 & # 2, 28