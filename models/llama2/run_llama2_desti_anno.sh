export TARGET_FOLDER=/remote-home/share/llama_v2
export MODEL_NAME=llama-2-13b

CUDA_VISIBLE_DEVICES=4,5 nohup torchrun \
--nproc_per_node 2 --master_port 12348 ./llama2_infer_desti_anno.py \
--ckpt_dir $TARGET_FOLDER/$MODEL_NAME \
--tokenizer_path $TARGET_FOLDER/tokenizer.model \
--mango_folder /remote-home/pli/mango \
--save_folder /remote-home/pli/mango/model_results/llama2_results_0721 \
--max_batch_size 8 > ../outs/llama2_desti_anno_a800.out 2>&1 & # 2, 28