export RWKV_JIT_ON=1
RWKV_DIR=/remote-home/pli/ChatRWKV
CKPT_DIR=/remote-home/pli/RWKV-LM/ckpts/rwkv-4-pile-14b/RWKV-4-Pile-14B-20230313-ctx8192-test1050

CUDA_VISIBLE_DEVICES=0 nohup python ./rwkv_infer_route.py \
--rwkv_dir $RWKV_DIR \
--ckpt_dir $CKPT_DIR \
--mango_folder /remote-home/pli/mango \
--save_folder /remote-home/pli/mango/model_results/rwkv_results_0705 \
--chunk_len 2048 \
--start_game_idx 0 \
--end_game_idx 3 >outs/rwkv_route_0_3_gpu0.out 2>&1 &