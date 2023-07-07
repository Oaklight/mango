export RWKV_JIT_ON=1
RWKV_DIR=/remote-home/pli/ChatRWKV
CKPT_DIR=/remote-home/pli/RWKV-LM/ckpts/rwkv-4-pile-14b/RWKV-4-Pile-14B-20230313-ctx8192-test1050

# CUDA_VISIBLE_DEVICES=0 nohup python ./rwkv_infer_route.py \
# --rwkv_dir $RWKV_DIR \
# --ckpt_dir $CKPT_DIR \
# --mango_folder /remote-home/pli/mango \
# --save_folder /remote-home/pli/mango/model_results/rwkv_results_0705 \
# --chunk_len 2048 \
# --start_game_idx 0 \
# --end_game_idx 3 >outs/rwkv_route_0_3_gpu0.out 2>&1 &


CUDA_VISIBLE_DEVICES=0 nohup python ./rwkv_infer_route.py --rwkv_dir $RWKV_DIR --ckpt_dir $CKPT_DIR --mango_folder /remote-home/pli/mango --save_folder /remote-home/pli/mango/model_results/rwkv_results_0705 --chunk_len 2048 --start_game_idx 0 --end_game_idx 3 > ../outs/rwkv_route_0_3_gpu0.out 2>&1
CUDA_VISIBLE_DEVICES=0 nohup python ./rwkv_infer_route.py --rwkv_dir $RWKV_DIR --ckpt_dir $CKPT_DIR --mango_folder /remote-home/pli/mango --save_folder /remote-home/pli/mango/model_results/rwkv_results_0705 --chunk_len 2048 --start_game_idx 0 --end_game_idx 3 > ../outs/rwkv_route_0_3_gpu0.out 2>&1
CUDA_VISIBLE_DEVICES=1 nohup python ./rwkv_infer_route.py --rwkv_dir $RWKV_DIR --ckpt_dir $CKPT_DIR --mango_folder /remote-home/pli/mango --save_folder /remote-home/pli/mango/model_results/rwkv_results_0705 --chunk_len 2048 --start_game_idx 6 --end_game_idx 9 > ../outs/rwkv_route_6_9_gpu1.out 2>&1
CUDA_VISIBLE_DEVICES=1 nohup python ./rwkv_infer_route.py --rwkv_dir $RWKV_DIR --ckpt_dir $CKPT_DIR --mango_folder /remote-home/pli/mango --save_folder /remote-home/pli/mango/model_results/rwkv_results_0705 --chunk_len 2048 --start_game_idx 9 --end_game_idx 12 > ../outs/rwkv_route_9_12_gpu1.out 2>&1
CUDA_VISIBLE_DEVICES=2 nohup python ./rwkv_infer_route.py --rwkv_dir $RWKV_DIR --ckpt_dir $CKPT_DIR --mango_folder /remote-home/pli/mango --save_folder /remote-home/pli/mango/model_results/rwkv_results_0705 --chunk_len 2048 --start_game_idx 12 --end_game_idx 15 > ../outs/rwkv_route_12_15_gpu2.out 2>&1
CUDA_VISIBLE_DEVICES=2 nohup python ./rwkv_infer_route.py --rwkv_dir $RWKV_DIR --ckpt_dir $CKPT_DIR --mango_folder /remote-home/pli/mango --save_folder /remote-home/pli/mango/model_results/rwkv_results_0705 --chunk_len 2048 --start_game_idx 48 --end_game_idx 51 > ../outs/rwkv_route_48_51_gpu2.out 2>&1
CUDA_VISIBLE_DEVICES=3 nohup python ./rwkv_infer_route.py --rwkv_dir $RWKV_DIR --ckpt_dir $CKPT_DIR --mango_folder /remote-home/pli/mango --save_folder /remote-home/pli/mango/model_results/rwkv_results_0705 --chunk_len 2048 --start_game_idx 18 --end_game_idx 21 > ../outs/rwkv_route_18_21_gpu3.out 2>&1
CUDA_VISIBLE_DEVICES=3 nohup python ./rwkv_infer_route.py --rwkv_dir $RWKV_DIR --ckpt_dir $CKPT_DIR --mango_folder /remote-home/pli/mango --save_folder /remote-home/pli/mango/model_results/rwkv_results_0705 --chunk_len 2048 --start_game_idx 21 --end_game_idx 24 > ../outs/rwkv_route_21_24_gpu3.out 2>&1
CUDA_VISIBLE_DEVICES=4 nohup python ./rwkv_infer_route.py --rwkv_dir $RWKV_DIR --ckpt_dir $CKPT_DIR --mango_folder /remote-home/pli/mango --save_folder /remote-home/pli/mango/model_results/rwkv_results_0705 --chunk_len 2048 --start_game_idx 24 --end_game_idx 27 > ../outs/rwkv_route_24_27_gpu4.out 2>&1
CUDA_VISIBLE_DEVICES=4 nohup python ./rwkv_infer_route.py --rwkv_dir $RWKV_DIR --ckpt_dir $CKPT_DIR --mango_folder /remote-home/pli/mango --save_folder /remote-home/pli/mango/model_results/rwkv_results_0705 --chunk_len 2048 --start_game_idx 27 --end_game_idx 30 > ../outs/rwkv_route_27_30_gpu4.out 2>&1
CUDA_VISIBLE_DEVICES=5 nohup python ./rwkv_infer_route.py --rwkv_dir $RWKV_DIR --ckpt_dir $CKPT_DIR --mango_folder /remote-home/pli/mango --save_folder /remote-home/pli/mango/model_results/rwkv_results_0705 --chunk_len 2048 --start_game_idx 30 --end_game_idx 33 > ../outs/rwkv_route_30_33_gpu5.out 2>&1
CUDA_VISIBLE_DEVICES=5 nohup python ./rwkv_infer_route.py --rwkv_dir $RWKV_DIR --ckpt_dir $CKPT_DIR --mango_folder /remote-home/pli/mango --save_folder /remote-home/pli/mango/model_results/rwkv_results_0705 --chunk_len 2048 --start_game_idx 33 --end_game_idx 36 > ../outs/rwkv_route_33_36_gpu5.out 2>&1
CUDA_VISIBLE_DEVICES=6 nohup python ./rwkv_infer_route.py --rwkv_dir $RWKV_DIR --ckpt_dir $CKPT_DIR --mango_folder /remote-home/pli/mango --save_folder /remote-home/pli/mango/model_results/rwkv_results_0705 --chunk_len 2048 --start_game_idx 36 --end_game_idx 39 > ../outs/rwkv_route_36_39_gpu6.out 2>&1
CUDA_VISIBLE_DEVICES=6 nohup python ./rwkv_infer_route.py --rwkv_dir $RWKV_DIR --ckpt_dir $CKPT_DIR --mango_folder /remote-home/pli/mango --save_folder /remote-home/pli/mango/model_results/rwkv_results_0705 --chunk_len 2048 --start_game_idx 39 --end_game_idx 42 > ../outs/rwkv_route_39_42_gpu6.out 2>&1
CUDA_VISIBLE_DEVICES=7 nohup python ./rwkv_infer_route.py --rwkv_dir $RWKV_DIR --ckpt_dir $CKPT_DIR --mango_folder /remote-home/pli/mango --save_folder /remote-home/pli/mango/model_results/rwkv_results_0705 --chunk_len 2048 --start_game_idx 42 --end_game_idx 45 > ../outs/rwkv_route_42_45_gpu7.out 2>&1
CUDA_VISIBLE_DEVICES=7 nohup python ./rwkv_infer_route.py --rwkv_dir $RWKV_DIR --ckpt_dir $CKPT_DIR --mango_folder /remote-home/pli/mango --save_folder /remote-home/pli/mango/model_results/rwkv_results_0705 --chunk_len 2048 --start_game_idx 45 --end_game_idx 48 > ../outs/rwkv_route_45_48_gpu7.out 2>&1