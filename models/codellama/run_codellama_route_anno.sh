#!/bin/sh

export TARGET_FOLDER=/home-nfs/pengli/workspace/projects/codellama/ckpts
export MODEL_NAME=CodeLlama-13b

MASTER_PORT=32345
START_GAME_IDX=0
END_GAME_IDX=1000

while [ $# -gt 0 ]; do
  case "$1" in
    --master_port)
      MASTER_PORT="$2"
      shift 2
      ;;
    --start_game_idx)
      START_GAME_IDX="$2"
      shift 2
      ;;
    --end_game_idx)
      END_GAME_IDX="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

torchrun \
--nproc_per_node 2 --master_port "$MASTER_PORT" ./codellama_infer_route_anno.py \
--ckpt_dir $TARGET_FOLDER/$MODEL_NAME \
--tokenizer_path $TARGET_FOLDER/$MODEL_NAME/tokenizer.model \
--mango_folder /home-nfs/pengli/workspace/projects/mango \
--save_folder /home-nfs/pengli/workspace/projects/mango/model_results/codellama_results_anno_1111 \
--max_batch_size 4 \
--start_game_idx "$START_GAME_IDX" \
--end_game_idx "$END_GAME_IDX"